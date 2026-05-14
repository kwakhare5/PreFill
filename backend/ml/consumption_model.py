from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta
from sqlalchemy import select
from backend.database.models import OrderItem, Order, ConsumptionModel
from backend.database.connection import async_session
import logging

logger = logging.getLogger(__name__)

class ConsumptionModeler:
    
    MIN_DATA_POINTS = 3     # Need at least 3 purchases to build a model
    MIN_CONFIDENCE = 0.30   # Only save models with ≥30% confidence
    
    async def build_model_for_item(self, household_id: str, item_id: str, item_name: str) -> dict | None:
        """
        Builds Prophet time-series model for a single item.
        Returns model data or None if insufficient data.
        """
        async with async_session() as db:
            # Fetch purchase history
            result = await db.execute(
                select(OrderItem.standard_quantity, Order.placed_at)
                .join(Order, Order.id == OrderItem.order_id)
                .where(Order.household_id == household_id)
                .where(OrderItem.item_id == item_id)
                .order_by(Order.placed_at.asc())
            )
            purchases = result.all()
        
        if len(purchases) < self.MIN_DATA_POINTS:
            logger.info(f"Insufficient data for {item_name}: only {len(purchases)} purchases")
            return None
        
        # Build Prophet dataframe
        df = pd.DataFrame({
            "ds": [p[1] for p in purchases],
            "y": [p[0] for p in purchases]
        })
        # Remove timezone for Prophet
        df["ds"] = pd.to_datetime(df["ds"]).dt.tz_localize(None)
        
        try:
            # Fit Prophet model
            model = Prophet(
                seasonality_mode='multiplicative',
                yearly_seasonality=False,
                weekly_seasonality=(len(purchases) >= 10),
                daily_seasonality=False,
                interval_width=0.80
            )
            
            # Suppress Prophet's logging
            import logging as log
            log.getLogger('prophet').setLevel(log.WARNING)
            log.getLogger('cmdstanpy').setLevel(log.WARNING)
            
            model.fit(df)
            
            # Predict future to get consumption rate
            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)
            
        except Exception as e:
            logger.error(f"Prophet failed for {item_name}: {e}")
            return None
        
        # Calculate derived metrics
        total_quantity = df["y"].sum()
        days_elapsed = max((df["ds"].max() - df["ds"].min()).days, 1)
        avg_daily = total_quantity / days_elapsed
        
        time_diffs = df["ds"].diff().dt.days.dropna()
        cycle_days = float(time_diffs.mean())
        
        last_purchase_date = purchases[-1][1]
        last_purchase_qty = purchases[-1][0]
        
        # Estimated depletion date
        if avg_daily > 0:
            days_remaining = last_purchase_qty / avg_daily
            depletion_date = last_purchase_date + timedelta(days=days_remaining)
        else:
            depletion_date = None
        
        # Confidence score (simplified: based on purchase consistency)
        confidence = min(1.0, len(purchases) / 10.0)
        
        return {
            "avg_daily_consumption": avg_daily,
            "consumption_cycle_days": cycle_days,
            "last_purchase_date": last_purchase_date,
            "last_purchase_quantity": last_purchase_qty,
            "estimated_depletion_date": depletion_date,
            "confidence_score": confidence,
            "data_points": len(purchases)
        }

    async def update_all_models(self, household_id: str):
        """
        Build/update models for all recurring items in a household.
        """
        async with async_session() as db:
            # Find all items purchased more than MIN_DATA_POINTS times
            result = await db.execute(
                select(OrderItem.item_id, OrderItem.item_name)
                .join(Order, Order.id == OrderItem.order_id)
                .where(Order.household_id == household_id)
                .group_by(OrderItem.item_id, OrderItem.item_name)
                .having(pd.io.sql.func.count(OrderItem.id) >= self.MIN_DATA_POINTS)
            )
            items = result.all()
            
            for item_id, item_name in items:
                model_data = await self.build_model_for_item(household_id, item_id, item_name)
                if not model_data:
                    continue
                
                # Update or insert into consumption_models
                stmt = select(ConsumptionModel).where(
                    ConsumptionModel.household_id == household_id,
                    ConsumptionModel.item_id == item_id
                )
                existing_res = await db.execute(stmt)
                existing = existing_res.scalar_one_or_none()
                
                if existing:
                    for key, value in model_data.items():
                        setattr(existing, key, value)
                    existing.updated_at = datetime.utcnow()
                else:
                    new_model = ConsumptionModel(
                        household_id=household_id,
                        item_id=item_id,
                        item_name=item_name,
                        **model_data
                    )
                    db.add(new_model)
            
            await db.commit()

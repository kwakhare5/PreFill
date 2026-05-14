from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database.connection import get_db
from backend.database.models import Household, Order, OrderItem
import httpx
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

router = APIRouter(prefix="/api/household", tags=["household"])

MCP_BASE_URL = os.getenv("MCP_BASE_URL", "http://localhost:3001")

async def get_or_create_household(user_id: str, db: AsyncSession):
    result = await db.execute(select(Household).where(Household.user_id == user_id))
    household = result.scalar_one_or_none()
    if not household:
        household = Household(user_id=user_id)
        db.add(household)
        await db.commit()
        await db.refresh(household)
    return household

def normalize_quantity(quantity: int, unit: str, standard_quantity: float = None) -> float:
    if standard_quantity:
        return standard_quantity
    return float(quantity)

async def sync_orders(household_id: str, user_id: str, db: AsyncSession):
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{MCP_BASE_URL}/get_instamart_orders",
                params={"user_id": user_id, "limit": 200}
            )
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            raise HTTPException(status_code=503, detail=f"Failed to fetch from MCP: {str(e)}")
    
    orders_synced = 0
    for raw_order in data["orders"]:
        # Check if already synced
        result = await db.execute(select(Order).where(Order.instamart_order_id == raw_order["order_id"]))
        if result.scalar_one_or_none():
            continue
        
        # Insert order
        new_order = Order(
            household_id=household_id,
            instamart_order_id=raw_order["order_id"],
            placed_at=datetime.fromisoformat(raw_order["placed_at"]),
            total_amount=raw_order["total"],
            raw_data=raw_order
        )
        db.add(new_order)
        await db.flush()  # Get ID without committing yet
        
        # Insert line items
        for item in raw_order["items"]:
            std_qty = normalize_quantity(item["quantity"], item.get("unit"), item.get("standard_quantity"))
            new_item = OrderItem(
                order_id=new_order.id,
                item_id=item["item_id"],
                item_name=item["item_name"],
                category=item.get("category"),
                quantity=item["quantity"],
                unit=item.get("unit"),
                standard_quantity=std_qty,
                price=item.get("price")
            )
            db.add(new_item)
        
        orders_synced += 1
    
    await db.commit()
    return orders_synced

@router.post("/{user_id}/sync")
async def sync_household_orders(user_id: str, db: AsyncSession = Depends(get_db)):
    household = await get_or_create_household(user_id, db)
    synced = await sync_orders(household.id, user_id, db)
    return {"message": f"Synced {synced} new orders", "household_id": str(household.id)}

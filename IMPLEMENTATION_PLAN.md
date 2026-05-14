# Instamart Intelligence — Detailed Implementation Plan
## Week-by-week, day-by-day execution roadmap

---

# HOW TO READ THIS DOCUMENT

This is not a list of tasks. It is a sequenced execution plan. Each step depends on the previous one. Do not skip ahead. The order matters because:

- You cannot build the prediction engine (Week 2) before you have data flowing (Week 1)
- You cannot build the WhatsApp bot (Week 3) before you have predictions to alert on
- You cannot record a convincing demo (Week 4) without all features working together

Each task has a **Why this matters** note explaining what breaks if you skip it, and a **Done when** definition so you know when to move on.

---

# PRE-WEEK: SETUP (Day 0 — 2-3 hours)

Before writing a single line of application code, set up your environment completely. Doing this later creates integration problems.

---

## Task 0.1 — Folder Structure

Create the exact project structure first. Empty folders are fine. You'll fill them in as you go.

```bash
mkdir instamart-intelligence
cd instamart-intelligence

# Backend
mkdir -p backend/{database/migrations,mcp,ml,agents,api/routes,notifications,seed,tests}

# Frontend
mkdir -p frontend/{app/{household,predictions,recipes,price-alerts},components,lib}

# Config files
touch backend/main.py
touch backend/config.py
touch .env.example
touch docker-compose.yml
touch README.md
```

**Why this matters:** Starting with clear structure prevents the "where does this file go?" decision fatigue that slows development mid-week.

**Done when:** `tree instamart-intelligence` shows all folders.

---

## Task 0.2 — Docker Compose for TimescaleDB

```yaml
# docker-compose.yml
version: '3.8'

services:
  timescaledb:
    image: timescale/timescaledb:latest-pg15
    container_name: instamart_db
    ports:
      - "5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: instamart_intelligence
    volumes:
      - timescale_data:/var/lib/postgresql/data

volumes:
  timescale_data:
```

```bash
docker-compose up -d
# Verify it's running
docker ps
# Should show timescale/timescaledb container running
```

**Done when:** `docker ps` shows the container running and `psql -h localhost -U postgres -d instamart_intelligence` connects successfully.

---

## Task 0.3 — Python Virtual Environment + Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install fastapi==0.110.0 \
    uvicorn[standard]==0.27.0 \
    sqlalchemy[asyncio]==2.0.28 \
    asyncpg==0.29.0 \
    alembic==1.13.1 \
    prophet==1.1.5 \
    pandas==2.2.0 \
    numpy==1.26.4 \
    scikit-learn==1.4.0 \
    langgraph==0.0.62 \
    langchain-anthropic==0.1.6 \
    anthropic==0.21.0 \
    twilio==8.13.0 \
    apscheduler==3.10.4 \
    pgvector==0.2.5 \
    python-dotenv==1.0.1 \
    httpx==0.26.0 \
    pydantic==2.6.3

# Save exact versions
pip freeze > requirements.txt
```

**Done when:** `python -c "import prophet, langgraph, anthropic"` runs without errors.

---

## Task 0.4 — Environment Variables

```bash
# .env.example (commit this)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost/instamart_intelligence
MCP_BASE_URL=http://localhost:3001
ANTHROPIC_API_KEY=your_key_here
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token
TWILIO_WHATSAPP_FROM=+14155238886

# .env (never commit this — add to .gitignore)
cp .env.example .env
# Fill in real values in .env
```

**Done when:** `.env` exists with real values, `.gitignore` includes `.env`.

---

## Task 0.5 — Initialize Git

```bash
git init
echo "venv/" >> .gitignore
echo ".env" >> .gitignore
echo "__pycache__/" >> .gitignore
echo "*.pyc" >> .gitignore
git add .
git commit -m "Project structure and environment setup"
```

**Done when:** First commit exists. You can push to GitHub now (proves you started work — useful for your Builders Club application).

---

---

# WEEK 1: DATA PIPELINE
## Goal: Order history flowing → Consumption models building

---

## Day 1 (Monday) — Database Schema + Models

### Task 1.1 — Create Database Tables

```python
# backend/database/models.py
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import DeclarativeBase, relationship
import uuid

class Base(DeclarativeBase):
    pass

class Household(Base):
    __tablename__ = "households"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), unique=True, nullable=False)
    phone_number = Column(String(20))
    composition = Column(String(50))           # solo, couple, family_small, family_large
    composition_confidence = Column(Float)
    intelligence_consent = Column(Boolean, default=False)
    notifications_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True))
    orders = relationship("Order", back_populates="household")

class Order(Base):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"))
    instamart_order_id = Column(String(255), unique=True)
    placed_at = Column(DateTime(timezone=True), nullable=False)
    total_amount = Column(Float)
    raw_data = Column(JSONB)
    household = relationship("Household", back_populates="orders")
    items = relationship("OrderItem", back_populates="order")

class OrderItem(Base):
    __tablename__ = "order_items"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id"))
    item_id = Column(String(255), nullable=False)
    item_name = Column(String(500), nullable=False)
    category = Column(String(100))
    quantity = Column(Integer)
    unit = Column(String(50))
    standard_quantity = Column(Float)          # normalized (500ml → 0.5L)
    price = Column(Float)
    order = relationship("Order", back_populates="items")

class ConsumptionModel(Base):
    __tablename__ = "consumption_models"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"))
    item_id = Column(String(255))
    item_name = Column(String(500))
    category = Column(String(100))
    avg_daily_consumption = Column(Float)
    consumption_cycle_days = Column(Float)
    last_purchase_date = Column(DateTime(timezone=True))
    last_purchase_quantity = Column(Float)
    estimated_depletion_date = Column(DateTime(timezone=True))
    confidence_score = Column(Float)
    data_points = Column(Integer)
    is_anomaly_excluded = Column(Boolean, default=False)
    updated_at = Column(DateTime(timezone=True))

class RestockAlert(Base):
    __tablename__ = "restock_alerts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"))
    item_ids = Column(JSONB)                   # list of item IDs in this alert
    message_sent = Column(Text)
    sent_at = Column(DateTime(timezone=True))
    status = Column(String(50), default='pending')   # pending/sent/acted/dismissed
    acted_at = Column(DateTime(timezone=True))
    order_id_placed = Column(String(255))

class PriceHistory(Base):
    __tablename__ = "price_history"
    # TimescaleDB hypertable — partitioned by recorded_at
    item_id = Column(String(255), primary_key=True)
    item_name = Column(String(500))
    recorded_at = Column(DateTime(timezone=True), primary_key=True)
    price = Column(Float)
    price_per_unit = Column(Float)

class Recipe(Base):
    __tablename__ = "recipes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    household_id = Column(UUID(as_uuid=True), ForeignKey("households.id"))
    name = Column(String(500))
    servings = Column(Integer)
    ingredients = Column(JSONB)
    cuisine = Column(String(100))
    pinned_for = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True))
```

After writing models, run Alembic to create the tables:
```bash
cd backend
alembic init migrations
# Edit alembic.ini to point to your database URL
# Edit migrations/env.py to import your Base and models
alembic revision --autogenerate -m "initial schema"
alembic upgrade head

# Enable TimescaleDB hypertable for price_history
psql -h localhost -U postgres -d instamart_intelligence \
  -c "SELECT create_hypertable('price_history', 'recorded_at', if_not_exists => TRUE);"
  
# Enable pgvector
psql -h localhost -U postgres -d instamart_intelligence \
  -c "CREATE EXTENSION IF NOT EXISTS vector;"
```

**Done when:** All tables exist in the database and `alembic current` shows the latest revision.

---

## Day 1 (Monday) — Mock MCP Server

### Task 1.2 — Build the Mock Swiggy MCP Server

This runs on port 3001 and pretends to be Swiggy's real API. You'll replace it with the real MCP when you get production access.

```python
# backend/mcp/mock_server.py
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
import os

app = FastAPI(title="Mock Swiggy Instamart MCP")

# In-memory store for mock orders — loaded from seed data file
MOCK_ORDERS = []
MOCK_CART = {"items": [], "cart_id": None}

@app.on_event("startup")
async def load_seed_data():
    global MOCK_ORDERS
    seed_file = "backend/seed/generated_orders.json"
    if os.path.exists(seed_file):
        with open(seed_file) as f:
            MOCK_ORDERS = json.load(f)
        print(f"Loaded {len(MOCK_ORDERS)} mock orders")

@app.get("/get_instamart_orders")
async def get_orders(user_id: str = "demo_user_001", limit: int = 100):
    return {
        "success": True,
        "user_id": user_id,
        "total_orders": len(MOCK_ORDERS),
        "orders": MOCK_ORDERS[-limit:]
    }

@app.post("/search_instamart_items")
async def search_items(body: dict):
    query = body.get("query", "").lower()
    # Simple mock: return relevant items based on query keyword
    MOCK_CATALOG = [
        {"id": "INS_001", "name": "Amul Taza Milk 1L", "price": 28, "price_per_unit": 28, "unit": "L", "category": "dairy"},
        {"id": "INS_002", "name": "Aashirvaad Atta 5kg", "price": 198, "price_per_unit": 39.6, "unit": "kg", "category": "staples"},
        {"id": "INS_003", "name": "Fortune Sunflower Oil 1L", "price": 127, "price_per_unit": 127, "unit": "L", "category": "staples"},
        {"id": "INS_004", "name": "India Gate Basmati Rice 5kg", "price": 310, "price_per_unit": 62, "unit": "kg", "category": "staples"},
        {"id": "INS_005", "name": "Nandini Eggs (Pack of 12)", "price": 84, "price_per_unit": 7, "unit": "piece", "category": "protein"},
        {"id": "INS_006", "name": "Tomatoes (500g)", "price": 29, "price_per_unit": 58, "unit": "kg", "category": "vegetables"},
        {"id": "INS_007", "name": "Onions (1kg)", "price": 42, "price_per_unit": 42, "unit": "kg", "category": "vegetables"},
        {"id": "INS_008", "name": "Amul Butter 500g", "price": 270, "price_per_unit": 540, "unit": "kg", "category": "dairy"},
        {"id": "INS_009", "name": "Amul Fresh Cream 200ml", "price": 55, "price_per_unit": 275, "unit": "L", "category": "dairy"},
        {"id": "INS_010", "name": "Tata Salt 1kg", "price": 28, "price_per_unit": 28, "unit": "kg", "category": "staples"},
    ]
    results = [item for item in MOCK_CATALOG if query in item["name"].lower() or query in item["category"].lower()]
    return {"items": results if results else MOCK_CATALOG[:3]}

class CartUpdate(BaseModel):
    items: list

@app.post("/update_instamart_cart")
async def update_cart(body: CartUpdate):
    import uuid
    MOCK_CART["cart_id"] = f"CART_{str(uuid.uuid4())[:8]}"
    MOCK_CART["items"] = body.items
    total = sum(item.get("price", 50) * item.get("quantity", 1) for item in body.items)
    return {"success": True, "cart_id": MOCK_CART["cart_id"], "items": body.items, "total": total}

@app.get("/get_instamart_cart")
async def get_cart():
    return {"success": True, **MOCK_CART}

class PlaceOrder(BaseModel):
    cart_id: str

@app.post("/place_instamart_order")
async def place_order(body: PlaceOrder):
    import uuid, random
    order_id = f"INS_{random.randint(10000, 99999)}"
    return {
        "success": True,
        "order_id": order_id,
        "cart_id": body.cart_id,
        "status": "placed",
        "estimated_delivery_minutes": random.randint(12, 20),
        "placed_at": datetime.now().isoformat()
    }

@app.get("/track_instamart_order/{order_id}")
async def track_order(order_id: str):
    return {
        "order_id": order_id,
        "status": "out_for_delivery",
        "estimated_arrival": "10-15 minutes"
    }
```

Run mock server: `uvicorn backend.mcp.mock_server:app --port 3001 --reload`

**Done when:** `curl http://localhost:3001/get_instamart_orders?user_id=demo_user_001` returns a JSON response.

---

## Day 2 (Tuesday) — Seed Data Generator

### Task 1.3 — Write and Run the Seed Script

This is the most important non-ML task. Take time to make the data realistic.

```python
# backend/seed/generate_orders.py
"""
Run: python -m backend.seed.generate_orders
Generates 4 months of realistic Indian household order history.
Output: backend/seed/generated_orders.json
"""

import json
import random
from datetime import datetime, timedelta

HOUSEHOLD_ITEMS = {
    "INS_001": {
        "name": "Amul Taza Milk 1L",
        "category": "dairy",
        "unit": "L",
        "pack_size": 1.0,
        "family_daily_use": 1.0,    # 1L per day for family of 4
        "base_price": 28,
        "price_variance": 0.05      # ±5% price variation
    },
    "INS_002": {
        "name": "Aashirvaad Atta 5kg",
        "category": "staples",
        "unit": "kg",
        "pack_size": 5.0,
        "family_daily_use": 0.30,   # 300g/day (6-8 rotis per meal x 2 meals)
        "base_price": 198,
        "price_variance": 0.10
    },
    "INS_003": {
        "name": "Fortune Sunflower Oil 1L",
        "category": "staples",
        "unit": "L",
        "pack_size": 1.0,
        "family_daily_use": 0.068,  # 68ml/day
        "base_price": 127,
        "price_variance": 0.15      # Oil prices fluctuate more
    },
    "INS_004": {
        "name": "India Gate Basmati Rice 5kg",
        "category": "staples",
        "unit": "kg",
        "pack_size": 5.0,
        "family_daily_use": 0.25,   # 250g/day
        "base_price": 310,
        "price_variance": 0.08
    },
    "INS_005": {
        "name": "Nandini Eggs (Pack of 12)",
        "category": "protein",
        "unit": "piece",
        "pack_size": 12.0,
        "family_daily_use": 2.5,    # 2-3 eggs/day for family
        "base_price": 84,
        "price_variance": 0.12
    },
    "INS_006": {
        "name": "Tomatoes (500g)",
        "category": "vegetables",
        "unit": "kg",
        "pack_size": 0.5,
        "family_daily_use": 0.15,
        "base_price": 20,
        "price_variance": 0.40      # Tomatoes are highly volatile!
    },
    "INS_007": {
        "name": "Onions (1kg)",
        "category": "vegetables",
        "unit": "kg",
        "pack_size": 1.0,
        "family_daily_use": 0.10,
        "base_price": 35,
        "price_variance": 0.35
    },
    "INS_008": {
        "name": "Amul Butter 500g",
        "category": "dairy",
        "unit": "kg",
        "pack_size": 0.5,
        "family_daily_use": 0.025,
        "base_price": 270,
        "price_variance": 0.05
    },
    "INS_009": {
        "name": "Tata Salt 1kg",
        "category": "staples",
        "unit": "kg",
        "pack_size": 1.0,
        "family_daily_use": 0.008,  # 8g/day — very slow consumption
        "base_price": 28,
        "price_variance": 0.03
    },
    "INS_010": {
        "name": "Britannia Bread (Large)",
        "category": "bakery",
        "unit": "piece",
        "pack_size": 1.0,
        "family_daily_use": 0.25,   # ~1 loaf every 4 days
        "base_price": 55,
        "price_variance": 0.04
    },
}

def generate_realistic_orders(months: int = 4, household_type: str = "family"):
    """
    Generates orders with realistic patterns:
    - Reorder happens 0-2 days AFTER predicted depletion (slight delay, human behavior)
    - Quantity varies ±15% (buy extra sometimes, or less)
    - Travel gap: no orders for 10 days in month 2
    - Guest spike: 3x milk in one order in month 3
    - Weekend clustering: slight preference for Saturday/Sunday orders
    """
    
    start_date = datetime.now() - timedelta(days=months * 30)
    end_date = datetime.now() - timedelta(days=1)
    
    # Track inventory (in standard units)
    inventory = {item_id: item["pack_size"] for item_id, item in HOUSEHOLD_ITEMS.items()}
    
    # Define anomaly windows
    travel_start = start_date + timedelta(days=45)
    travel_end = travel_start + timedelta(days=10)
    guest_date = start_date + timedelta(days=75)
    
    # Collect: {date_str: [items to order that day]}
    pending_orders_by_date = {}
    
    current_date = start_date
    while current_date < end_date:
        
        # Skip travel window
        is_traveling = travel_start <= current_date <= travel_end
        
        for item_id, item in HOUSEHOLD_ITEMS.items():
            daily_use = item["family_daily_use"]
            
            # Guest spike: on guest_date, milk consumption was 3x
            if abs((current_date - guest_date).days) < 2 and item_id == "INS_001":
                daily_use = daily_use * 3
            
            # Consume inventory
            noise = random.uniform(0.85, 1.15)
            if not is_traveling:
                inventory[item_id] = max(0, inventory[item_id] - daily_use * noise)
            
            # Check if needs reorder (2 days of stock or less)
            buffer_days = 2
            if inventory[item_id] <= daily_use * buffer_days and not is_traveling:
                # Human delay: reorder 0-2 days after the system would say to
                reorder_delay = random.randint(0, 2)
                reorder_date = current_date + timedelta(days=reorder_delay)
                date_key = reorder_date.strftime("%Y-%m-%d")
                
                # Quantity variation: ±20%
                quantity_multiplier = random.uniform(0.8, 1.2)
                packs_to_buy = max(1, round(item["pack_size"] * quantity_multiplier))
                
                if date_key not in pending_orders_by_date:
                    pending_orders_by_date[date_key] = []
                
                pending_orders_by_date[date_key].append({
                    "item_id": item_id,
                    "item_name": item["name"],
                    "quantity": packs_to_buy,
                    "standard_quantity": packs_to_buy * item["pack_size"],
                    "unit": item["unit"],
                    "category": item["category"],
                    "price": item["base_price"] * packs_to_buy * random.uniform(1 - item["price_variance"], 1 + item["price_variance"])
                })
                
                # Restock inventory
                inventory[item_id] += packs_to_buy * item["pack_size"]
        
        current_date += timedelta(days=1)
    
    # Convert to order objects
    orders = []
    order_counter = 1
    
    for date_str in sorted(pending_orders_by_date.keys()):
        items = pending_orders_by_date[date_str]
        if not items:
            continue
        
        # Sometimes combine nearby orders (within 2 days) into one — realistic clustering
        order_hour = random.choice([9, 10, 11, 18, 19, 20, 21])  # Morning or evening
        order_minute = random.randint(0, 59)
        
        orders.append({
            "order_id": f"INS_MOCK_{order_counter:04d}",
            "user_id": "demo_user_001",
            "placed_at": f"{date_str}T{order_hour:02d}:{order_minute:02d}:00+05:30",
            "items": items,
            "total": round(sum(i["price"] for i in items), 2),
            "status": "delivered"
        })
        order_counter += 1
    
    return orders


if __name__ == "__main__":
    print("Generating seed data...")
    orders = generate_realistic_orders(months=4)
    
    output_path = "backend/seed/generated_orders.json"
    with open(output_path, "w") as f:
        json.dump(orders, f, indent=2)
    
    print(f"✅ Generated {len(orders)} orders over 4 months")
    print(f"   Saved to {output_path}")
    print(f"   Date range: {orders[0]['placed_at'][:10]} → {orders[-1]['placed_at'][:10]}")
    
    # Summary stats
    item_counts = {}
    for order in orders:
        for item in order["items"]:
            item_counts[item["item_name"]] = item_counts.get(item["item_name"], 0) + 1
    
    print("\nItem purchase frequency:")
    for name, count in sorted(item_counts.items(), key=lambda x: -x[1]):
        print(f"   {name}: {count} times")
```

Run it:
```bash
python -m backend.seed.generate_orders
# Then restart mock server to load the data
```

**Done when:** `generated_orders.json` exists with 60-100 orders, and the mock MCP endpoint returns them.

---

## Day 2-3 (Tue-Wed) — Data Ingestion Pipeline

### Task 1.4 — Order Sync Service

This is the bridge between MCP (Swiggy's data) and your database.

```python
# backend/api/routes/household.py
from fastapi import APIRouter, Depends
import httpx
from datetime import datetime

router = APIRouter(prefix="/api/household", tags=["household"])

async def sync_orders(household_id: str, user_id: str):
    """
    Pull orders from MCP, normalize them, store in DB.
    Safe to run multiple times (idempotent — won't duplicate orders).
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{MCP_BASE_URL}/get_instamart_orders",
            params={"user_id": user_id, "limit": 200}
        )
        data = response.json()
    
    orders_synced = 0
    for raw_order in data["orders"]:
        # Check if already synced
        existing = await db.fetch_one(
            "SELECT id FROM orders WHERE instamart_order_id = $1",
            raw_order["order_id"]
        )
        if existing:
            continue
        
        # Insert order
        order_id = await db.execute("""
            INSERT INTO orders (household_id, instamart_order_id, placed_at, total_amount, raw_data)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id
        """, household_id, raw_order["order_id"],
            datetime.fromisoformat(raw_order["placed_at"]),
            raw_order["total"],
            raw_order
        )
        
        # Insert line items (with unit normalization)
        for item in raw_order["items"]:
            std_qty = normalize_quantity(item["quantity"], item.get("unit"), item.get("standard_quantity"))
            await db.execute("""
                INSERT INTO order_items (order_id, item_id, item_name, category, quantity, unit, standard_quantity, price)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
            """, order_id, item["item_id"], item["item_name"], item.get("category"),
                item["quantity"], item.get("unit"), std_qty, item.get("price"))
        
        orders_synced += 1
    
    return orders_synced


def normalize_quantity(quantity: int, unit: str, standard_quantity: float = None) -> float:
    """
    Convert pack quantities to standard units.
    e.g., 2 packs of 500ml → 1.0 L
    """
    if standard_quantity:
        return standard_quantity
    # Fallback: treat as 1 unit
    return float(quantity)


@router.post("/{user_id}/sync")
async def sync_household_orders(user_id: str):
    household = await get_or_create_household(user_id)
    synced = await sync_orders(str(household["id"]), user_id)
    return {"message": f"Synced {synced} new orders", "household_id": str(household["id"])}
```

**Done when:** `POST /api/household/demo_user_001/sync` returns `{"message": "Synced 87 new orders"}` (or whatever count your seed data has).

---

## Day 3-4 (Wed-Thu) — Consumption Model Builder

### Task 1.5 — Prophet Model per Item

```python
# backend/ml/consumption_model.py

from prophet import Prophet
import pandas as pd
from datetime import datetime, timedelta
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
        # Fetch purchase history
        purchases = await db.fetch_all("""
            SELECT oi.standard_quantity, o.placed_at
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.household_id = $1 AND oi.item_id = $2
            ORDER BY o.placed_at ASC
        """, household_id, item_id)
        
        if len(purchases) < self.MIN_DATA_POINTS:
            logger.info(f"Insufficient data for {item_name}: only {len(purchases)} purchases")
            return None
        
        # Build Prophet dataframe
        df = pd.DataFrame({
            "ds": [p["placed_at"] for p in purchases],
            "y": [p["standard_quantity"] for p in purchases]
        })
        df["ds"] = pd.to_datetime(df["ds"])
        
        try:
            # Fit Prophet model
            model = Prophet(
                seasonality_mode='multiplicative',
                yearly_seasonality=False,
                weekly_seasonality=(len(purchases) >= 10),  # Only if enough data
                daily_seasonality=False,
                interval_width=0.80                          # 80% confidence intervals
            )
            
            # Suppress Prophet's stdout logging
            import logging as log
            log.getLogger('prophet').setLevel(log.WARNING)
            log.getLogger('cmdstanpy').setLevel(log.WARNING)
            
            model.fit(df)
            
        except Exception as e:
            logger.error(f"Prophet failed for {item_name}: {e}")
            return None
        
        # --- Calculate derived metrics ---
        
        # 1. Average daily consumption
        total_quantity = df["y"].sum()
        days_elapsed = max((df["ds"].max() - df["ds"].min()).days, 1)
        avg_daily = total_quantity / days_elapsed
        
        # 2. Typical purchase cycle (days between purchases)
        time_diffs = df["ds"].diff().dt.days.dropna()
        cycle_days = float(time_diffs.mean())
        
        # 3. Last purchase details
        last_row = purchases[-1]
        last_purchase_date = last_row["placed_at"]
        last_purchase_qty = last_row["standard_quantity"]
        
        # 4. Estimated depletion date
        if avg_daily > 0:
            days_remaining = last_purchase_qty / avg_daily
            depletion_date = last_purchase_date + timedelta(days=days_remaining)
        else:
            depletion_date = None
        
        # 5. Confidence score
        # Based on: regularity of purchase intervals + number of data points
        cycle_std = float(time_diffs.std()) if len(time_diffs) > 1 else 30
        regularity_score = max(0, 1 - (cycle_std / 14))    # Normalize to 14-day std = 0 confidence
        data_score = min(1.0, len(purchases) / 20)          # 20+ data points = max data confidence
        confidence = (regularity_score * 0.6) + (data_score * 0.4)  # Weighted average
        
        if confidence < self.MIN_CONFIDENCE:
            return None
        
        return {
            "household_id": household_id,
            "item_id": item_id,
            "item_name": item_name,
            "avg_daily_consumption": round(avg_daily, 4),
            "consumption_cycle_days": round(cycle_days, 1),
            "last_purchase_date": last_purchase_date,
            "last_purchase_quantity": last_purchase_qty,
            "estimated_depletion_date": depletion_date,
            "confidence_score": round(confidence, 3),
            "data_points": len(purchases),
            "updated_at": datetime.now()
        }
    
    async def rebuild_all_models(self, household_id: str) -> dict:
        """Rebuild all consumption models for a household"""
        # Get all unique items ordered by this household
        items = await db.fetch_all("""
            SELECT DISTINCT oi.item_id, oi.item_name, COUNT(*) as purchase_count
            FROM order_items oi
            JOIN orders o ON o.id = oi.order_id
            WHERE o.household_id = $1
            GROUP BY oi.item_id, oi.item_name
            HAVING COUNT(*) >= 3
            ORDER BY purchase_count DESC
        """, household_id)
        
        results = {"built": 0, "skipped": 0, "errors": 0}
        
        for item in items:
            try:
                model_data = await self.build_model_for_item(
                    household_id, item["item_id"], item["item_name"]
                )
                if model_data:
                    # Upsert into consumption_models
                    await db.execute("""
                        INSERT INTO consumption_models 
                            (household_id, item_id, item_name, avg_daily_consumption, 
                             consumption_cycle_days, last_purchase_date, last_purchase_quantity,
                             estimated_depletion_date, confidence_score, data_points, updated_at)
                        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
                        ON CONFLICT (household_id, item_id) 
                        DO UPDATE SET 
                            avg_daily_consumption = EXCLUDED.avg_daily_consumption,
                            confidence_score = EXCLUDED.confidence_score,
                            estimated_depletion_date = EXCLUDED.estimated_depletion_date,
                            updated_at = NOW()
                    """, *list(model_data.values()))
                    results["built"] += 1
                else:
                    results["skipped"] += 1
            except Exception as e:
                logger.error(f"Error building model for {item['item_name']}: {e}")
                results["errors"] += 1
        
        return results
```

**Done when:** `POST /api/household/demo_user_001/rebuild-models` returns `{"built": 8, "skipped": 2, "errors": 0}` and the `consumption_models` table has rows with `confidence_score > 0.5`.

---

## Day 4-5 (Thu-Fri) — FastAPI Main + Basic Endpoints

### Task 1.6 — Wire up FastAPI app

```python
# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api.routes import household, predictions, restock, recipes
from backend.notifications.scheduler import start_scheduler

app = FastAPI(title="Instamart Intelligence API", version="1.0.0")

app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:3000"], allow_methods=["*"], allow_headers=["*"])

app.include_router(household.router)
app.include_router(predictions.router)
app.include_router(restock.router)
app.include_router(recipes.router)

@app.on_event("startup")
async def startup():
    await init_db()
    start_scheduler()

@app.get("/health")
async def health():
    return {"status": "ok", "version": "1.0.0"}
```

**End of Week 1 state check:**
- [ ] Database running with all tables
- [ ] Seed data generated (80-100 realistic orders)
- [ ] Mock MCP server running on port 3001
- [ ] Order sync working (data flows from MCP to DB)
- [ ] Consumption models built for 8+ items with real confidence scores
- [ ] FastAPI running on port 8000 with `/health` endpoint

---

---

# WEEK 2: PREDICTION ENGINE
## Goal: Accurate forecasts + smart anomaly handling + alert triggers

---

## Day 6 (Monday) — Anomaly Detection

### Task 2.1 — Travel + Guest + Dietary Change Detection

```python
# backend/ml/anomaly_detector.py

from datetime import datetime, timedelta
from collections import defaultdict

class AnomalyDetector:
    
    def detect_travel(self, order_dates: list[datetime]) -> dict:
        """
        Look for gaps > 5 days between consecutive orders.
        These likely represent travel periods.
        """
        if len(order_dates) < 2:
            return {"detected": False}
        
        sorted_dates = sorted(order_dates)
        gaps = []
        
        for i in range(1, len(sorted_dates)):
            gap_days = (sorted_dates[i] - sorted_dates[i-1]).days
            if gap_days >= 5:
                gaps.append({
                    "start": sorted_dates[i-1],
                    "end": sorted_dates[i],
                    "duration_days": gap_days
                })
        
        if not gaps:
            return {"detected": False, "type": "travel"}
        
        return {
            "detected": True,
            "type": "travel",
            "gaps": gaps,
            "total_travel_days": sum(g["duration_days"] for g in gaps),
            "travel_frequency_per_year": len(gaps) * (365 / max((sorted_dates[-1] - sorted_dates[0]).days, 1)) * len(gaps)
        }
    
    def detect_guest_visit(self, item_id: str, purchase_history: list, baseline_quantity: float) -> dict:
        """
        Identify orders where quantity purchased was >2x the baseline.
        These should be excluded from consumption model to avoid inflating daily averages.
        """
        spikes = []
        for purchase in purchase_history:
            ratio = purchase["standard_quantity"] / max(baseline_quantity, 0.001)
            if ratio >= 2.5:
                spikes.append({
                    "date": purchase["placed_at"],
                    "quantity": purchase["standard_quantity"],
                    "baseline": baseline_quantity,
                    "spike_factor": round(ratio, 1)
                })
        
        if spikes:
            return {
                "detected": True,
                "type": "guest_visit",
                "spike_events": spikes,
                "recommendation": "exclude_from_model",
                "spike_order_ids": [s["date"] for s in spikes]
            }
        return {"detected": False, "type": "guest_visit"}
    
    def detect_dietary_change(self, category_monthly_counts: dict) -> dict:
        """
        If any food category drops >60% in the most recent month vs prior average.
        
        Input: {"dairy": [4, 3, 5, 1], "protein": [6, 7, 5, 6]}
        The last value in each list is the most recent month.
        """
        changes = []
        
        for category, monthly_counts in category_monthly_counts.items():
            if len(monthly_counts) < 3:
                continue
            
            prior_avg = sum(monthly_counts[:-1]) / len(monthly_counts[:-1])
            recent = monthly_counts[-1]
            
            if prior_avg == 0:
                continue
            
            drop_pct = ((prior_avg - recent) / prior_avg) * 100
            
            if drop_pct > 60:
                changes.append({
                    "category": category,
                    "drop_percentage": round(drop_pct, 1),
                    "prior_avg_orders_per_month": round(prior_avg, 1),
                    "recent_month_orders": recent
                })
        
        return {
            "detected": bool(changes),
            "type": "dietary_change",
            "changes": changes,
            "recommendation": "confirm_with_user" if changes else None
        }
```

---

## Day 7 (Tuesday) — Confidence Scoring + Alert Trigger Logic

### Task 2.2 — Alert Trigger Service

```python
# backend/api/routes/restock.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

ALERT_THRESHOLD_DAYS = 2    # Alert when 2 or fewer days of stock remain
MIN_CONFIDENCE = 0.50        # Only alert if model confidence > 50%

async def check_depletions_for_household(household_id: str) -> list:
    """
    Returns list of items that need restocking alerts.
    Applies confidence threshold and deduplication (don't re-alert within 24h).
    """
    # Get models that are close to depletion
    depleting_items = await db.fetch_all("""
        SELECT cm.*, 
               EXTRACT(EPOCH FROM (cm.estimated_depletion_date - NOW())) / 86400 as days_until_depletion
        FROM consumption_models cm
        WHERE cm.household_id = $1
          AND cm.confidence_score >= $2
          AND cm.estimated_depletion_date IS NOT NULL
          AND cm.estimated_depletion_date BETWEEN NOW() AND NOW() + INTERVAL '$3 days'
        ORDER BY cm.estimated_depletion_date ASC
    """, household_id, MIN_CONFIDENCE, ALERT_THRESHOLD_DAYS)
    
    # Filter out items that were recently alerted (within last 24 hours)
    recently_alerted = await db.fetch_all("""
        SELECT DISTINCT unnest(item_ids::text[]) as item_id
        FROM restock_alerts
        WHERE household_id = $1
          AND sent_at > NOW() - INTERVAL '24 hours'
          AND status IN ('sent', 'acted')
    """, household_id)
    
    recently_alerted_ids = {r["item_id"] for r in recently_alerted}
    
    return [
        item for item in depleting_items 
        if item["item_id"] not in recently_alerted_ids
    ]


async def daily_depletion_check_all():
    """Run every morning at 8am for all households"""
    households = await db.fetch_all("""
        SELECT h.id, h.phone_number 
        FROM households h
        WHERE h.notifications_enabled = TRUE
          AND h.phone_number IS NOT NULL
          AND h.intelligence_consent = TRUE
    """)
    
    total_alerts_sent = 0
    for household in households:
        depleting = await check_depletions_for_household(str(household["id"]))
        if depleting:
            await send_depletion_alert(household, depleting)
            total_alerts_sent += 1
    
    logger.info(f"Daily check complete: {total_alerts_sent} alerts sent to {len(households)} households")
```

---

## Day 7-8 (Tue-Wed) — Household Profiler

### Task 2.3 — Infer Household Composition

```python
# backend/ml/household_profiler.py

BENCHMARKS = {
    "solo": {
        "milk_daily_L": 0.25,
        "atta_daily_kg": 0.07,
        "eggs_daily": 0.70,
        "oil_daily_L": 0.020
    },
    "couple": {
        "milk_daily_L": 0.50,
        "atta_daily_kg": 0.15,
        "eggs_daily": 1.50,
        "oil_daily_L": 0.040
    },
    "family_small": {   # 3-4 people
        "milk_daily_L": 1.00,
        "atta_daily_kg": 0.30,
        "eggs_daily": 2.50,
        "oil_daily_L": 0.068
    },
    "family_large": {   # 5+ people
        "milk_daily_L": 2.00,
        "atta_daily_kg": 0.60,
        "eggs_daily": 5.00,
        "oil_daily_L": 0.13
    }
}

ITEM_TO_METRIC = {
    "INS_001": "milk_daily_L",
    "INS_002": "atta_daily_kg",
    "INS_005": "eggs_daily",
    "INS_003": "oil_daily_L"
}

DISPLAY_NAMES = {
    "solo": "Solo (1 person)",
    "couple": "Couple (2 people)",
    "family_small": "Family (3-4 people)",
    "family_large": "Large Family (5+)"
}

async def infer_household_composition(household_id: str) -> dict:
    models = await db.fetch_all(
        "SELECT item_id, avg_daily_consumption FROM consumption_models WHERE household_id = $1",
        household_id
    )
    
    observed = {m["item_id"]: m["avg_daily_consumption"] for m in models}
    
    scores = {}
    for hh_type, benchmarks in BENCHMARKS.items():
        score_components = []
        for item_id, metric in ITEM_TO_METRIC.items():
            if item_id in observed and metric in benchmarks:
                ratio = observed[item_id] / benchmarks[metric]
                component_score = max(0, 1 - abs(1 - ratio))
                score_components.append(component_score)
        
        scores[hh_type] = sum(score_components) / max(len(score_components), 1)
    
    best_type = max(scores, key=scores.get)
    best_confidence = scores[best_type]
    
    return {
        "composition": best_type,
        "display_name": DISPLAY_NAMES[best_type],
        "confidence": round(best_confidence, 2),
        "all_scores": scores
    }
```

---

## Day 8-9 (Wed-Thu) — LangGraph Restock Agent

### Task 2.4 — Full Agent Graph

This is the most complex piece. Build it carefully with clear state management.

```python
# backend/agents/restock_agent.py
from langgraph.graph import StateGraph, END
from anthropic import Anthropic
from typing import TypedDict, Optional
import json

anthropic = Anthropic()

class RestockState(TypedDict):
    household_id: str
    depleting_items: list
    stage: str                          # "alert" | "awaiting_reply" | "building_cart" | "done"
    user_message: Optional[str]
    confirmed_items: list
    cart_id: Optional[str]
    cart_total: Optional[float]
    order_id: Optional[str]
    response_message: str
    error: Optional[str]


def format_items_for_prompt(items: list) -> str:
    lines = []
    for item in items:
        days = round(item.get("days_until_depletion", 1), 1)
        confidence = int(item["confidence_score"] * 100)
        lines.append(f"- {item['item_name']}: {confidence}% likely low ({days} days remaining)")
    return "\n".join(lines)


async def generate_alert_message(state: RestockState) -> RestockState:
    """Generate a natural WhatsApp alert message using Claude"""
    items_text = format_items_for_prompt(state["depleting_items"])
    
    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": f"""You are a smart household assistant for Swiggy Instamart.
            
The following items are likely running low in this household:
{items_text}

Write a WhatsApp message (under 80 words) that:
1. Lists the top 3 items with confidence percentages
2. Is friendly but brief
3. Ends with: "Reply YES to reorder all, or tell me which ones."
4. Does not use excessive emojis (max 2)
5. Mentions this is based on their purchase pattern

Write ONLY the message, nothing else."""
        }]
    )
    
    state["response_message"] = response.content[0].text
    state["stage"] = "awaiting_reply"
    return state


async def parse_user_reply(state: RestockState) -> RestockState:
    """Parse what the user said and determine which items to reorder"""
    user_msg = (state.get("user_message") or "").strip().upper()
    
    # Simple yes/no detection
    if user_msg in ["YES", "Y", "REORDER", "ORDER ALL", "PLACE ORDER", "YES PLEASE", "OK", "OKAY"]:
        state["confirmed_items"] = state["depleting_items"]
        state["stage"] = "building_cart"
        return state
    
    if user_msg in ["NO", "NOPE", "CANCEL", "SKIP", "NOT NOW", "LATER"]:
        state["confirmed_items"] = []
        state["response_message"] = "Got it! I'll check again tomorrow. 👍"
        state["stage"] = "done"
        return state
    
    # Partial response — use Claude to parse intent
    items_text = "\n".join([f"- {item['item_name']}" for item in state["depleting_items"]])
    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        messages=[{
            "role": "user",
            "content": f"""The user was asked if they want to reorder these grocery items:
{items_text}

Their reply was: "{state['user_message']}"

Return a JSON array of item names the user wants to reorder. 
Return an empty array [] if they don't want anything.
Return the complete list if they said something like "all" or "everything".
Return ONLY the JSON array, no explanation.
Example: ["Amul Taza Milk 1L", "Fortune Sunflower Oil 1L"]"""
        }]
    )
    
    try:
        wanted_names = json.loads(response.content[0].text)
        state["confirmed_items"] = [
            item for item in state["depleting_items"]
            if any(wanted.lower() in item["item_name"].lower() for wanted in wanted_names)
        ]
        state["stage"] = "building_cart" if state["confirmed_items"] else "done"
    except:
        state["response_message"] = "Sorry, I didn't understand. Reply YES to reorder all, or NO to skip."
        state["stage"] = "awaiting_reply"
    
    return state


async def build_cart(state: RestockState) -> RestockState:
    """Search for items on Instamart and build a cart"""
    if not state["confirmed_items"]:
        state["response_message"] = "Nothing to order. I'll check again tomorrow!"
        state["stage"] = "done"
        return state
    
    cart_items = []
    async with httpx.AsyncClient() as client:
        for item in state["confirmed_items"]:
            # Search for the item
            search_resp = await client.post(
                f"{MCP_BASE_URL}/search_instamart_items",
                json={"query": item["item_name"]}
            )
            results = search_resp.json()
            if results.get("items"):
                best_match = results["items"][0]
                cart_items.append({
                    "item_id": best_match["id"],
                    "item_name": best_match["name"],
                    "quantity": 1,
                    "price": best_match["price"]
                })
        
        # Create cart
        cart_resp = await client.post(
            f"{MCP_BASE_URL}/update_instamart_cart",
            json={"items": cart_items}
        )
        cart_data = cart_resp.json()
        
        state["cart_id"] = cart_data["cart_id"]
        state["cart_total"] = cart_data.get("total", 0)
    
    item_names = [i["item_name"] for i in cart_items]
    state["response_message"] = (
        f"Cart ready: {', '.join(item_names[:3])}{'...' if len(item_names) > 3 else ''}. "
        f"Total: ₹{state['cart_total']:.0f}. Reply CONFIRM to place order."
    )
    state["stage"] = "awaiting_confirm"
    return state


async def place_order(state: RestockState) -> RestockState:
    """Place the final order"""
    async with httpx.AsyncClient() as client:
        order_resp = await client.post(
            f"{MCP_BASE_URL}/place_instamart_order",
            json={"cart_id": state["cart_id"]}
        )
        order_data = order_resp.json()
        
        if order_data.get("success"):
            state["order_id"] = order_data["order_id"]
            eta = order_data.get("estimated_delivery_minutes", 15)
            state["response_message"] = (
                f"✅ Order placed! Arriving in ~{eta} mins. "
                f"Order #{state['order_id']}"
            )
        else:
            state["error"] = "Order placement failed"
            state["response_message"] = "⚠️ Couldn't place order. Please try on the Instamart app."
    
    state["stage"] = "done"
    return state


# Build the graph
graph = StateGraph(RestockState)
graph.add_node("generate_alert", generate_alert_message)
graph.add_node("parse_reply", parse_user_reply)
graph.add_node("build_cart", build_cart)
graph.add_node("place_order", place_order)

graph.set_entry_point("generate_alert")
graph.add_edge("generate_alert", END)     # First invocation: just generate the alert

# Second invocation (after user replies):
graph.add_edge("parse_reply", "build_cart")
graph.add_conditional_edges("build_cart", lambda s: "place_order" if s.get("cart_id") else END)
graph.add_edge("place_order", END)

restock_agent = graph.compile()
```

**Done when:** You can call the agent with test data and it generates a natural WhatsApp message.

---

## Day 10 (Friday) — Week 2 Integration Test

Run an end-to-end test of the full pipeline:

```bash
# 1. Sync orders
curl -X POST http://localhost:8000/api/household/demo_user_001/sync

# 2. Rebuild models
curl -X POST http://localhost:8000/api/household/demo_user_001/rebuild-models

# 3. Trigger manual depletion check
curl -X POST http://localhost:8000/api/restock/check-now?household_id=demo_user_001

# 4. View predictions
curl http://localhost:8000/api/predictions/demo_user_001

# Expected response:
# {
#   "household": {...},
#   "depleting_soon": [
#     {"item_name": "Amul Taza Milk 1L", "days_remaining": 1.2, "confidence": 0.84},
#     {"item_name": "Fortune Sunflower Oil 1L", "days_remaining": 1.8, "confidence": 0.87}
#   ]
# }
```

**End of Week 2 state check:**
- [ ] Depletion predictions returning for multiple items
- [ ] Confidence scores between 0.5-0.95 (not too high = fake, not too low = useless)
- [ ] Anomaly detector correctly identifying the travel gap in seed data
- [ ] Household profiler returning "family_small" with >70% confidence for demo data
- [ ] LangGraph agent generating a natural-sounding WhatsApp message

---

---

# WEEK 3: INTERFACE & NOTIFICATIONS
## Goal: WhatsApp bot + Next.js dashboard working end-to-end

---

## Day 11-12 (Mon-Tue) — WhatsApp Integration

### Task 3.1 — Twilio Sandbox Setup

1. Sign up at https://www.twilio.com
2. Get a free account — they give you $15 credit, enough for 1000s of messages in development
3. Go to Messaging → Try it out → Send a WhatsApp message
4. Follow the Twilio sandbox setup — send "join [sandbox-word]" from your WhatsApp to +1-415-523-8886
5. Your number is now in the sandbox — you can send/receive messages for development

```python
# backend/notifications/whatsapp.py
from fastapi import APIRouter, Request, Form
from twilio.rest import Client
from twilio.twiml.messaging_response import MessagingResponse
import os

router = APIRouter(prefix="/webhook", tags=["webhooks"])
twilio_client = Client(os.getenv("TWILIO_ACCOUNT_SID"), os.getenv("TWILIO_AUTH_TOKEN"))
TWILIO_FROM = f"whatsapp:{os.getenv('TWILIO_WHATSAPP_FROM')}"


async def send_whatsapp(to_number: str, message: str):
    """Send a WhatsApp message via Twilio"""
    twilio_client.messages.create(
        from_=TWILIO_FROM,
        body=message,
        to=f"whatsapp:{to_number}"
    )


@router.post("/whatsapp")
async def whatsapp_webhook(
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(...)
):
    """
    Twilio calls this endpoint when user sends a WhatsApp message.
    Twilio requires a TwiML response.
    """
    phone = From.replace("whatsapp:", "")
    user_message = Body.strip()
    
    # Look up household
    household = await db.fetch_one(
        "SELECT * FROM households WHERE phone_number = $1", phone
    )
    
    if not household:
        resp = MessagingResponse()
        resp.message("Hi! Please set up your Instamart Intelligence account at the app first.")
        return Response(content=str(resp), media_type="application/xml")
    
    # Handle STOP command
    if user_message.upper() == "STOP":
        await db.execute(
            "UPDATE households SET notifications_enabled = FALSE WHERE id = $1",
            household["id"]
        )
        resp = MessagingResponse()
        resp.message("You've been unsubscribed from Instamart Intelligence alerts. Reply START to re-enable.")
        return Response(content=str(resp), media_type="application/xml")
    
    # Get pending alert for this household
    pending_alert = await db.fetch_one("""
        SELECT * FROM restock_alerts
        WHERE household_id = $1 AND status = 'sent'
        ORDER BY sent_at DESC LIMIT 1
    """, household["id"])
    
    # Run LangGraph agent with user's reply
    depleting_items = []
    if pending_alert:
        depleting_items = await get_items_from_alert(pending_alert)
    
    result = await restock_agent.ainvoke({
        "household_id": str(household["id"]),
        "depleting_items": depleting_items,
        "stage": "parse_reply",
        "user_message": user_message,
        "confirmed_items": [],
        "response_message": ""
    })
    
    # Update alert status if order was placed
    if result.get("order_id") and pending_alert:
        await db.execute("""
            UPDATE restock_alerts 
            SET status = 'acted', acted_at = NOW(), order_id_placed = $1
            WHERE id = $2
        """, result["order_id"], pending_alert["id"])
    
    # Respond via TwiML
    resp = MessagingResponse()
    resp.message(result["response_message"])
    return Response(content=str(resp), media_type="application/xml")
```

For local testing with Twilio, use ngrok to expose localhost:
```bash
# Install ngrok, then:
ngrok http 8000
# Copy the https://xxxx.ngrok.io URL
# In Twilio sandbox settings, set webhook URL to: https://xxxx.ngrok.io/webhook/whatsapp
```

**Done when:** You can send "YES" to your Twilio sandbox number and get back a cart confirmation message.

---

## Day 12-14 (Tue-Thu) — Next.js Dashboard

### Task 3.2 — Initialize Next.js + Key Pages

```bash
npx create-next-app@latest frontend --typescript --tailwind --app
cd frontend
npm install recharts lucide-react axios date-fns
```

Build the 4 key pages in this order:

**Page 1: Dashboard Home (`/`)**
Shows: Household profile card, depletion countdown cards, recent alert history

**Page 2: Predictions Timeline (`/predictions`)**
Shows: All modeled items sorted by depletion date, confidence bars, historical accuracy table

**Page 3: Recipe Planner (`/recipes`)**  
Shows: Recipe search box, ingredient checker, missing items cart

**Page 4: Price Alerts (`/price-alerts`)**
Shows: Commodity price charts (recharts line chart), spike/dip alerts, substitution suggestions

Dashboard design principle: The most important thing on the home page is the depletion countdown. A user should be able to open the app and within 3 seconds know "oil runs out in 2 days, milk in 4 days." Everything else is secondary.

---

## Day 14 (Thu) — API Endpoints for Dashboard

```python
# backend/api/routes/predictions.py

@router.get("/{household_id}")
async def get_predictions(household_id: str):
    """Main dashboard data endpoint"""
    
    models = await db.fetch_all("""
        SELECT *, 
            EXTRACT(EPOCH FROM (estimated_depletion_date - NOW())) / 86400 as days_remaining
        FROM consumption_models
        WHERE household_id = $1
          AND confidence_score >= 0.4
        ORDER BY estimated_depletion_date ASC NULLS LAST
    """, household_id)
    
    household = await db.fetch_one(
        "SELECT * FROM households WHERE id = $1", household_id
    )
    
    # Categorize items by urgency
    critical = [m for m in models if m["days_remaining"] and m["days_remaining"] <= 1]
    soon = [m for m in models if m["days_remaining"] and 1 < m["days_remaining"] <= 3]
    upcoming = [m for m in models if m["days_remaining"] and 3 < m["days_remaining"] <= 7]
    
    return {
        "household": {
            "id": str(household["id"]),
            "composition": household["composition"],
            "tracked_since": household["created_at"].isoformat() if household["created_at"] else None,
            "items_modeled": len(models)
        },
        "summary": {
            "critical_count": len(critical),
            "soon_count": len(soon),
            "upcoming_count": len(upcoming)
        },
        "depleting_soon": [dict(m) for m in (critical + soon + upcoming)[:10]],
        "all_models": [dict(m) for m in models]
    }
```

**End of Week 3 state check:**
- [ ] WhatsApp webhook receiving messages from Twilio
- [ ] YES reply triggers cart build + order placement (mock)
- [ ] Order confirmation message sent back to WhatsApp
- [ ] Dashboard shows depletion cards with real data
- [ ] All 4 dashboard pages render without errors

---

---

# WEEK 4: RECIPE + PRICE + DEMO
## Goal: Polish all features, generate great demo data, record video

---

## Day 15-16 (Mon-Tue) — Recipe Agent

### Task 4.1 — Recipe-to-Cart Feature

```python
# backend/agents/recipe_agent.py
import json
from anthropic import Anthropic

anthropic = Anthropic()

async def recipe_to_cart(recipe_name: str, servings: int, household_id: str) -> dict:
    """Full recipe → pantry check → missing items cart"""
    
    # Step 1: Parse recipe ingredients with Claude
    response = anthropic.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": f"""List all ingredients for "{recipe_name}" for {servings} people.
For Indian recipes, use standard Indian ingredient names as you'd find in a grocery app.

Return ONLY a JSON array with this exact structure, no other text:
[
  {{"name": "basmati rice", "quantity": 400, "unit": "g", "optional": false}},
  {{"name": "onions", "quantity": 3, "unit": "piece", "optional": false}}
]

Units must be one of: g, kg, ml, L, piece, tbsp, tsp"""
        }]
    )
    
    ingredients = json.loads(response.content[0].text)
    
    # Step 2: Get estimated pantry state
    consumption_models = await db.fetch_all("""
        SELECT item_id, item_name, last_purchase_date, last_purchase_quantity, avg_daily_consumption
        FROM consumption_models WHERE household_id = $1
    """, household_id)
    
    # Estimate remaining stock for each tracked item
    pantry = {}
    for model in consumption_models:
        days_since_purchase = (datetime.now() - model["last_purchase_date"]).days
        estimated_remaining = max(0, model["last_purchase_quantity"] - (days_since_purchase * model["avg_daily_consumption"]))
        pantry[model["item_name"].lower()] = {
            "item_id": model["item_id"],
            "estimated_remaining": estimated_remaining,
            "unit": "standard"
        }
    
    # Step 3: Find missing items
    have = []
    need = []
    
    for ingredient in ingredients:
        if ingredient.get("optional"):
            continue
        
        # Fuzzy match ingredient against pantry
        ingredient_lower = ingredient["name"].lower()
        pantry_match = None
        for pantry_item_name in pantry:
            if ingredient_lower in pantry_item_name or pantry_item_name in ingredient_lower:
                pantry_match = pantry[pantry_item_name]
                break
        
        if pantry_match and pantry_match["estimated_remaining"] > 0:
            have.append({
                "name": ingredient["name"],
                "quantity": ingredient["quantity"],
                "unit": ingredient["unit"],
                "in_pantry": True
            })
        else:
            need.append({
                "name": ingredient["name"],
                "quantity": ingredient["quantity"],
                "unit": ingredient["unit"],
                "in_pantry": False
            })
    
    # Step 4: Estimate cost of missing items
    total_cost = 0
    cart_items = []
    async with httpx.AsyncClient() as client:
        for item in need:
            search_resp = await client.post(
                f"{MCP_BASE_URL}/search_instamart_items",
                json={"query": item["name"]}
            )
            results = search_resp.json()
            if results.get("items"):
                match = results["items"][0]
                total_cost += match["price"]
                cart_items.append(match)
    
    return {
        "recipe": recipe_name,
        "servings": servings,
        "you_have": have,
        "you_need": need,
        "cart_items": cart_items,
        "estimated_cost": round(total_cost, 2),
        "ready_to_cook": len(need) == 0
    }
```

---

## Day 16-17 (Tue-Wed) — Price Tracker

### Task 4.2 — Commodity Price Tracking

```python
# backend/agents/price_agent.py

VOLATILE_COMMODITIES = [
    ("INS_006", "tomatoes"),
    ("INS_007", "onions"),
    ("INS_003", "sunflower oil"),
    ("INS_002", "atta wheat flour"),
    ("INS_004", "rice basmati"),
]

async def track_and_alert():
    """Called daily by scheduler"""
    for item_id, search_query in VOLATILE_COMMODITIES:
        # Get current price
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                f"{MCP_BASE_URL}/search_instamart_items",
                json={"query": search_query}
            )
            items = resp.json().get("items", [])
        
        if not items:
            continue
        
        current_price = items[0]["price_per_unit"]
        item_name = items[0]["name"]
        
        # Store price
        await db.execute(
            "INSERT INTO price_history (item_id, item_name, recorded_at, price_per_unit) VALUES ($1, $2, NOW(), $3)",
            item_id, item_name, current_price
        )
        
        # Get 30-day average
        avg = await db.fetch_val("""
            SELECT AVG(price_per_unit) FROM price_history
            WHERE item_id = $1 AND recorded_at > NOW() - INTERVAL '30 days'
        """, item_id)
        
        if not avg:
            continue
        
        pct_change = ((current_price - avg) / avg) * 100
        
        if abs(pct_change) > 25:
            alert_type = "spike" if pct_change > 0 else "dip"
            await notify_all_households_about_price(item_name, alert_type, pct_change, current_price, avg)
```

---

## Day 17-18 (Wed-Thu) — Demo Preparation

### Task 4.3 — Generate Demo-Quality Seed Data

Re-run seed script with tweaks to make the demo impressive:

Key things to ensure in your seed data:
1. Milk: exactly 2.1 days cycle ± small variance — makes "Your household uses 1L milk every 2.1 days" statement possible
2. Oil: exactly 14-15 day cycle — makes the prediction story clear
3. Travel gap: days 45-55 have zero orders (should be visible as a gap in the UI)
4. Tomato price: last 7 days in price_history should show a spike (add manual rows)
5. Last oil purchase should be exactly 12-13 days ago so it shows as "running low today" during demo

Run prediction accuracy verification:
```bash
# Check accuracy of your predictions against seed data
python -m backend.tests.verify_prediction_accuracy
# Should output: "Avg prediction error: 1.3 days across 8 items"
```

### Task 4.4 — Demo Video Recording Checklist

Before recording:
- [ ] Fresh seed data loaded
- [ ] All services running: DB, Mock MCP, FastAPI, Next.js
- [ ] WhatsApp sandbox connected to your phone
- [ ] Dashboard showing real predictions (not demo/placeholder text)
- [ ] Phone charged, Do Not Disturb ON except Twilio number
- [ ] Screen recording software ready (OBS or QuickTime)
- [ ] 1080p resolution, clean desktop

Record in one continuous take if possible. Cuts make it look less like a working demo. 3-4 minutes is ideal.

---

## Day 19 (Friday) — Swiggy Application + Polish

### Task 4.5 — Builders Club Application

Before submitting:
- [ ] GitHub repo is public and README explains the project clearly
- [ ] Demo video uploaded to YouTube (unlisted is fine)
- [ ] All MCP API names mentioned explicitly in application
- [ ] Business impact framed in Swiggy's language (GMV, retention, churn)
- [ ] "Built working localhost prototype" mentioned
- [ ] Demo video link included

**Application tip:** Lead with the Blinkit competition threat. Swiggy's product team thinks about this every day. The fact that your project directly addresses their #1 competitive concern is the hook.

---

# APPENDIX: QUICK REFERENCE

## Running all services

```bash
# Terminal 1: Database
docker-compose up

# Terminal 2: Mock MCP Server
uvicorn backend.mcp.mock_server:app --port 3001 --reload

# Terminal 3: Main API
uvicorn backend.main:app --port 8000 --reload

# Terminal 4: Frontend
cd frontend && npm run dev

# Terminal 5: ngrok (for Twilio webhook)
ngrok http 8000
```

## Key test commands

```bash
# Full pipeline test (run these in order)
curl -X POST http://localhost:8000/api/household/demo_user_001/sync
curl -X POST http://localhost:8000/api/household/demo_user_001/rebuild-models
curl http://localhost:8000/api/predictions/demo_user_001
curl -X POST http://localhost:8000/api/restock/check-now?household_id=demo_user_001
curl -X POST "http://localhost:8000/api/recipes/parse" -H "Content-Type: application/json" -d '{"recipe":"dal makhani","servings":4,"household_id":"demo_user_001"}'
```

## Database queries for debugging

```sql
-- Check consumption models
SELECT item_name, avg_daily_consumption, confidence_score, 
       estimated_depletion_date,
       EXTRACT(EPOCH FROM (estimated_depletion_date - NOW()))/86400 as days_remaining
FROM consumption_models 
WHERE household_id = (SELECT id FROM households WHERE user_id = 'demo_user_001')
ORDER BY estimated_depletion_date;

-- Check order count per item
SELECT item_name, COUNT(*) as orders, SUM(standard_quantity) as total_qty
FROM order_items oi
JOIN orders o ON o.id = oi.order_id
JOIN households h ON h.id = o.household_id
WHERE h.user_id = 'demo_user_001'
GROUP BY item_name
ORDER BY orders DESC;

-- Check alerts sent
SELECT sent_at, status, acted_at FROM restock_alerts 
WHERE household_id = (SELECT id FROM households WHERE user_id = 'demo_user_001')
ORDER BY sent_at DESC;
```

from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime
import json
import os
import uuid
import random

app = FastAPI(title="Mock Swiggy Instamart MCP")

# In-memory store for mock orders — loaded from seed data file
MOCK_ORDERS = []
MOCK_CART = {"items": [], "cart_id": None}

@app.on_event("startup")
async def load_seed_data():
    global MOCK_ORDERS
    seed_file = os.path.join(os.path.dirname(__file__), "..", "seed", "generated_orders.json")
    if os.path.exists(seed_file):
        with open(seed_file) as f:
            MOCK_ORDERS = json.load(f)
        print(f"Loaded {len(MOCK_ORDERS)} mock orders")
    else:
        print(f"Seed file not found at {seed_file}. Please run generate_orders.py first.")

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

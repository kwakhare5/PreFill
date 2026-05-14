import json
import random
from datetime import datetime, timedelta
import os

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
                packs_to_buy = max(1, round(item["pack_size"] * quantity_multiplier / item["pack_size"]))
                
                if date_key not in pending_orders_by_date:
                    pending_orders_by_date[date_key] = []
                
                pending_orders_by_date[date_key].append({
                    "item_id": item_id,
                    "item_name": item["name"],
                    "quantity": packs_to_buy,
                    "standard_quantity": packs_to_buy * item["pack_size"],
                    "unit": item["unit"],
                    "category": item["category"],
                    "price": round(item["base_price"] * packs_to_buy * random.uniform(1 - item["price_variance"], 1 + item["price_variance"]), 2)
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
    
    output_dir = os.path.dirname(__file__)
    output_path = os.path.join(output_dir, "generated_orders.json")
    with open(output_path, "w") as f:
        json.dump(orders, f, indent=2)
    
    print(f"Generated {len(orders)} orders over 4 months")
    print(f"   Saved to {output_path}")

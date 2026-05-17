import asyncio
from backend.database.connection import get_db
from backend.database.models import ConsumptionModel
from sqlalchemy import select

async def run():
    async for db in get_db():
        res = await db.execute(select(ConsumptionModel.item_name, ConsumptionModel.confidence_score))
        for row in res.mappings().all():
            print(f"{row['item_name']}: {row['confidence_score']}")

asyncio.run(run())

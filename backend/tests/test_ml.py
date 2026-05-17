import asyncio
from backend.database.connection import get_db
from backend.ml.consumption_model import ConsumptionModeler
from backend.api.routes.household import get_or_create_household

async def run():
    async for db in get_db():
        household = await get_or_create_household('demo_user_001', db)
        modeler = ConsumptionModeler()
        res = await modeler.rebuild_all_models(str(household.id), db)
        print(res)

asyncio.run(run())

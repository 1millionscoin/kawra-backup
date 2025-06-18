# init_db.py

import asyncio
from app.core.db import Base, engine
from app.models import user, balance, order, deposit_address, nft, pool

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database initialized.")

if __name__ == "__main__":
    asyncio.run(init())

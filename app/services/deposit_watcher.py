import asyncio, decimal, logging
from sqlalchemy import select
from ..core.db import SessionLocal
from ..models.deposit_address import DepositAddress
from ..models.balance import Balance
from ..services.kawra_rpc import _rpc
from ..models.user import User

log = logging.getLogger("deposit_watcher")

async def credit_loop():
    while True:
        try:
            txs = _rpc("listtransactions", "*", 200, 0, True)  # Fixed: Removed await
            async with SessionLocal() as db:
                for tx in txs:
                    if tx["category"] != "receive":
                        continue
                    addr = tx["address"]
                    amt = decimal.Decimal(str(tx["amount"]))
                    dep = await db.scalar(select(DepositAddress).where(DepositAddress.address == addr))
                    if not dep:
                        continue
                    bal = await db.scalar(select(Balance).where(Balance.user_id == dep.user_id, Balance.asset_id == "KAWRA"))
                    if not bal:
                        bal = Balance(user_id=dep.user_id, asset_id="KAWRA", amount=0)
                        db.add(bal)
                    bal.amount += amt
                await db.commit()
        except Exception as e:
            log.error("credit_loop error: %s", e)
        await asyncio.sleep(30)

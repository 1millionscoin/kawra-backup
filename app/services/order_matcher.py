import asyncio, decimal
from sqlalchemy import select
from ..core.db import SessionLocal
from ..models.order import Order
from ..models.balance import Balance

async def match_loop():
    while True:
        async with SessionLocal() as db:
            buys = (await db.execute(select(Order).where(Order.side=="BUY", Order.open==True))).scalars().all()
            sells = (await db.execute(select(Order).where(Order.side=="SELL", Order.open==True))).scalars().all()
            for buy in buys:
                for sell in sells:
                    if buy.base_id != sell.base_id or buy.quote_id != sell.quote_id:
                        continue
                    if buy.price < sell.price:
                        continue
                    trade_qty = min(buy.qty - buy.filled, sell.qty - sell.filled)
                    if trade_qty <= 0:
                        continue
                    await _settle(db, buy, sell, trade_qty, sell.price)
                    if buy.filled >= buy.qty:
                        buy.open = False
                    if sell.filled >= sell.qty:
                        sell.open = False
            await db.commit()
        await asyncio.sleep(3)

async def _settle(db, buy, sell, qty, price):
    cost = qty * price

    async def bal(uid, asset):
        return (await db.execute(
            select(Balance).where(Balance.user_id == uid, Balance.asset_id == asset))
        ).scalar_one_or_none()

    b_base = await bal(buy.user_id, buy.base_id)
    b_quote = await bal(buy.user_id, buy.quote_id)
    s_base = await bal(sell.user_id, sell.base_id)
    s_quote = await bal(sell.user_id, sell.quote_id)
    if not all([b_base, b_quote, s_base, s_quote]):
        return
    if b_quote.amount < cost or s_base.amount < qty:
        return
    b_base.amount += qty
    b_quote.amount -= cost
    s_base.amount -= qty
    s_quote.amount += cost
    buy.filled += qty
    sell.filled += qty

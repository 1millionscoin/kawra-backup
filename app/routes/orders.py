from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, condecimal
from decimal import Decimal
from sqlalchemy import select
from ..core.db import SessionLocal
from ..models.order import Order
from ..models.balance import Balance
from .auth import current_user

router = APIRouter(prefix="/orders", tags=["orders"])

class OrderIn(BaseModel):
    side: str
    base_id: str
    quote_id: str
    price: condecimal(gt=0)
    qty: condecimal(gt=0)

@router.post("/")
async def place(o: OrderIn, user=Depends(current_user)):
    async with SessionLocal() as db:
        bal = await db.scalar(select(Balance).where(Balance.user_id==user.id, Balance.asset_id==o.quote_id))
        cost = Decimal(o.price) * Decimal(o.qty)
        if o.side=="BUY" and (not bal or bal.amount < cost):
            raise HTTPException(400, "No funds")
        if o.side=="SELL":
            bal_s = await db.scalar(select(Balance).where(Balance.user_id==user.id, Balance.asset_id==o.base_id))
            if not bal_s or bal_s.amount < Decimal(o.qty):
                raise HTTPException(400, "No asset")
        order = Order(user_id=user.id, **o.dict())
        db.add(order)
        await db.commit()
        return {"order_id": order.id}

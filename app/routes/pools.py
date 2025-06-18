from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, condecimal
from decimal import Decimal
from ..services.pools import create_pool, swap
from .auth import current_user

router = APIRouter(prefix="/pools", tags=["pools"])

class PoolIn(BaseModel):
    token_id: str
    kawra_amt: condecimal(gt=0)
    token_amt: condecimal(gt=0)

@router.post("/create")
async def create(body: PoolIn, user=Depends(current_user)):
    try:
        return await create_pool(user, body.token_id, Decimal(body.kawra_amt), Decimal(body.token_amt))
    except Exception as e:
        raise HTTPException(400, str(e))

class SwapIn(BaseModel):
    side: str
    amount_in: condecimal(gt=0)
    min_out: condecimal(gt=0)

@router.post("/{pool_id}/swap")
async def swap_endpoint(pool_id: int, body: SwapIn, user=Depends(current_user)):
    try:
        return await swap(user, pool_id, body.side, Decimal(body.amount_in), Decimal(body.min_out))
    except Exception as e:
        raise HTTPException(400, str(e))

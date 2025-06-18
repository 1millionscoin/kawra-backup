from fastapi import APIRouter, Depends
from ..routes.auth import current_user
from ..services.address import new_deposit_address

router = APIRouter(prefix="/wallet", tags=["wallet"])

@router.post("/address")
async def fresh_address(user=Depends(current_user)):
    addr = await new_deposit_address(user)
    return {"address": addr}

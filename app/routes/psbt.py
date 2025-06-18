from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from ..routes.auth import current_user
from ..services.psbt import sweep_psbt

router = APIRouter(prefix="/psbt", tags=["psbt"])

class SweepReq(BaseModel):
    dest: str

@router.post("/sweep")
async def sweep(body: SweepReq, user=Depends(current_user)):
    try:
        psbt = await sweep_psbt(user.id, body.dest)
        return {"psbt": psbt}
    except Exception as e:
        raise HTTPException(400, str(e))

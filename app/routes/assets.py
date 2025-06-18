from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from ..services.nft import mint_nft
from ..services.token import create_token
from ..services.ipfs import add_file
from .auth import current_user

router = APIRouter(prefix="/assets", tags=["assets"])

@router.post("/nft/mint")
async def mint(file: UploadFile = File(...), user=Depends(current_user)):
    try:
        data = await file.read()
        return mint_nft(data, file.filename)
    except Exception as e:
        raise HTTPException(400, str(e))

@router.post("/token/create")
async def token(name: str, symbol: str, decimals: int, supply: int,
                logo: UploadFile|None = None, user=Depends(current_user)):
    logo_bytes = await logo.read() if logo else None
    try:
        return create_token(name, symbol, decimals, supply, logo_bytes)
    except Exception as e:
        raise HTTPException(400, str(e))

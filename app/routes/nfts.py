from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, condecimal
from decimal import Decimal
from sqlalchemy import select
from ..core.db import SessionLocal
from ..models.nft import NFTListing
from ..models.balance import Balance
from .auth import current_user

router = APIRouter(prefix="/nft", tags=["nft"])

class ListIn(BaseModel):
    nft_id: str
    price: condecimal(gt=0)

@router.post("/list")
async def list_nft(body: ListIn, user=Depends(current_user)):
    async with SessionLocal() as db:
        listing = NFTListing(nft_id=body.nft_id, owner_id=user.id, price=Decimal(body.price))
        db.add(listing)
        await db.commit()
        return {"listing_id": listing.id}

@router.post("/buy/{listing_id}")
async def buy(listing_id: int, user=Depends(current_user)):
    async with SessionLocal() as db:
        l = await db.get(NFTListing, listing_id)
        if not l or not l.active:
            raise HTTPException(404, "Listing")
        if l.owner_id == user.id:
            raise HTTPException(400, "Self buy")
        bal = await db.scalar(select(Balance).where(Balance.user_id==user.id, Balance.asset_id=="KAWRA"))
        if not bal or bal.amount < l.price:
            raise HTTPException(400, "Funds")
        bal.amount -= l.price
        seller_bal = await db.scalar(select(Balance).where(Balance.user_id==l.owner_id, Balance.asset_id=="KAWRA"))
        if not seller_bal:
            seller_bal = Balance(user_id=l.owner_id, asset_id="KAWRA", amount=0)
            db.add(seller_bal)
        seller_bal.amount += l.price
        l.owner_id = user.id
        l.active = False
        await db.commit()
        return {"status":"purchased"}

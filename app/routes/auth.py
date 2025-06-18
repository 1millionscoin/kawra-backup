
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel
from sqlalchemy import select
from ..core.db import SessionLocal
from ..services.auth import hash_pw, verify_pw, make_token, parse_token
from ..models.user import User
from ..models.deposit_address import DepositAddress
from ..services.hd import generate_seed, derive_address
from ..services.kawra_rpc import _rpc
from ..core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])

class UserIn(BaseModel):
    email: str
    password: str

async def current_user(authorization: str = Header(...)):
    try:
        token = authorization.replace("Bearer ", "")
        uid = parse_token(token)
    except Exception:
        raise HTTPException(401, "Invalid token")
    async with SessionLocal() as db:
        user = await db.get(User, uid)
        if not user:
            raise HTTPException(401, "User not found")
        return user

async def _create_watch_addr(xpub: str, idx: int):
    addr = derive_address(xpub, idx)
    desc = f"addr({addr})"
    _rpc("importdescriptors", [{"desc": desc, "timestamp": "now", "label": f"dep-{idx}", "watchonly": True}])
    return addr

@router.post("/register")
async def register(body: UserIn):
    mnemonic, xprv, xpub = generate_seed()
    async with SessionLocal() as db:
        if await db.scalar(select(User).where(User.email==body.email)):
            raise HTTPException(400, "Email exists")
        user = User(email=body.email, pw_hash=hash_pw(body.password),
                    xpub=xpub, next_index=1)
        # derive first deposit address index 0
        addr0 = derive_address(xpub, 0)
        user.first_addr = addr0
        db.add(user)
        await db.flush()
        db.add(DepositAddress(user_id=user.id, address=addr0, hd_index=0))
        await db.commit()
        # import watch-only
        _rpc("importaddress", addr0, f"dep-{user.id}", False)
        return {"token": make_token(user.id),
                "mnemonic": mnemonic,
                "deposit_address": addr0}
@router.post("/login")
async def login(body: UserIn):
    async with SessionLocal() as db:
        user = await db.scalar(select(User).where(User.email==body.email))
        if not user or not verify_pw(body.password, user.pw_hash):
            raise HTTPException(401, "Bad creds")
        return {"token": make_token(user.id)}

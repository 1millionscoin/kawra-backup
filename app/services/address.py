from sqlalchemy import select
from ..core.db import SessionLocal
from ..models.user import User
from ..models.deposit_address import DepositAddress
from ..services.hd import derive_address
from ..services.kawra_rpc import _rpc

async def new_deposit_address(user: User):
    async with SessionLocal() as db:
        # refresh user
        u = await db.get(User, user.id)
        idx = u.next_index
        addr = derive_address(u.xpub, idx)
        db.add(DepositAddress(user_id=u.id, address=addr, hd_index=idx))
        u.next_index += 1
        await db.commit()
        _rpc("importaddress", addr, f"dep-{u.id}-{idx}", False)
        return addr

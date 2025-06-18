from decimal import Decimal
from sqlalchemy import select
from ..core.db import SessionLocal
from ..models.deposit_address import DepositAddress
from ..services.kawra_rpc import _rpc

async def sweep_psbt(user_id: int, dest_address: str):
    # Identify UTXOs from user's deposit addresses
    addresses = []
    async with SessionLocal() as db:
        deps = (await db.execute(select(DepositAddress.address).where(DepositAddress.user_id==user_id))).scalars().all()
        addresses.extend(deps)
    if not addresses:
        raise ValueError("No deposit addresses")
    utxos = [u for u in _rpc("listunspent", 0) if u["address"] in addresses]
    if not utxos:
        raise ValueError("No UTXOs")
    inputs = [{"txid": u["txid"], "vout": u["vout"]} for u in utxos]
    total = sum(u["amount"] for u in utxos)
    outputs = {dest_address: total}
    psbt = _rpc("walletcreatefundedpsbt", inputs, outputs, 0, {"includeWatching": True, "subtractFeeFromOutputs":[dest_address]})["psbt"]
    return psbt

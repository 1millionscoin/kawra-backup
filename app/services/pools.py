import decimal
from sqlalchemy import select
from ..core.db import SessionLocal
from ..models.balance import Balance
from ..models.pool import Pool
from .kawra_rpc import listunspent, createrawtx, fundrawtx, signrawtx, sendrawtx
from ..core.config import settings

LOCK_FEE = decimal.Decimal("0.0001")

async def create_pool(user, token_id, kawra_amt, token_amt):
    async with SessionLocal() as db:
        b_k = await db.scalar(select(Balance).where(Balance.user_id==user.id, Balance.asset_id=="KAWRA"))
        b_t = await db.scalar(select(Balance).where(Balance.user_id==user.id, Balance.asset_id==token_id))
        if not b_k or b_k.amount < kawra_amt:
            raise ValueError("No KAWRA")
        if not b_t or b_t.amount < token_amt:
            raise ValueError("No token")
        b_k.amount -= kawra_amt
        b_t.amount -= token_amt

        commit = f"{settings.LOCK_TAG}{token_id}|{kawra_amt}|{token_amt}"
        if len(commit) > 80:
            raise ValueError("Commit too big")
        utxo = next(u for u in listunspent() if u["amount"] > LOCK_FEE)
        ins = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
        outs = {"data": commit.encode().hex()}
        tx = createrawtx(ins, outs)
        tx = fundrawtx(tx)
        tx = signrawtx(tx)
        txid = sendrawtx(tx)
        pool = Pool(token_id=token_id, reserve_kawra=kawra_amt, reserve_token=token_amt, tx_lock=txid)
        db.add(pool)
        await db.commit()
        return {"pool_id": pool.id, "tx_lock": txid}

async def swap(user, pool_id, side, amount_in, min_out):
    async with SessionLocal() as db:
        pool = await db.get(Pool, pool_id)
        if not pool:
            raise ValueError("Pool missing")
        if side == "KAWRA→TOKEN":
            r_in, r_out = pool.reserve_kawra, pool.reserve_token
            asset_in, asset_out = "KAWRA", pool.token_id
        else:
            r_in, r_out = pool.reserve_token, pool.reserve_kawra
            asset_in, asset_out = pool.token_id, "KAWRA"
        amount_in_fee = amount_in * decimal.Decimal("0.997")
        amount_out = (amount_in_fee * r_out) / (r_in + amount_in_fee)
        if amount_out < min_out:
            raise ValueError("Slippage")
        bal_in = await db.scalar(select(Balance).where(Balance.user_id==user.id, Balance.asset_id==asset_in))
        bal_out = await db.scalar(select(Balance).where(Balance.user_id==user.id, Balance.asset_id==asset_out))
        if not bal_in or bal_in.amount < amount_in:
            raise ValueError("Funds")
        if not bal_out:
            bal_out = Balance(user_id=user.id, asset_id=asset_out, amount=0)
            db.add(bal_out)
        bal_in.amount -= amount_in
        bal_out.amount += amount_out
        if side == "KAWRA→TOKEN":
            pool.reserve_kawra += amount_in
            pool.reserve_token -= amount_out
        else:
            pool.reserve_token += amount_in
            pool.reserve_kawra -= amount_out
        await db.commit()
        return {"amount_out": float(amount_out)}

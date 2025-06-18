from ..core.config import settings
from .ipfs import add_file
from .kawra_rpc import getnewaddress, listunspent, createrawtx, fundrawtx, signrawtx, sendrawtx

def create_token(name: str, symbol: str, decimals: int, supply: int, logo_bytes: bytes | None = None):
    if "|" in symbol or len(symbol) > 8:
        raise ValueError("Bad symbol")
    cid = add_file(logo_bytes, f"{symbol}.png") if logo_bytes else ""
    meta = f"{symbol}|{decimals}|{supply}"
    payload = f"{settings.TOKEN_TAG}{meta}"
    if cid:
        payload += f"|{cid}"
    if len(payload) > 80:
        raise ValueError("OP_RETURN too long")
    issuer = getnewaddress(f"{symbol}-issuer")
    utxo = next(u for u in listunspent() if u["amount"] > settings.NETWORK_FEE)
    ins = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
    outs = {issuer: round(settings.DUST_AMOUNT,8), "data": payload.encode().hex()}
    tx = createrawtx(ins, outs)
    tx = fundrawtx(tx)
    tx = signrawtx(tx)
    txid = sendrawtx(tx)
    return {"txid": txid, "token_id": f"{txid}:0", "issuer": issuer, "cid": cid or None}

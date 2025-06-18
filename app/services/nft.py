import uuid
from ..core.config import settings
from .ipfs import add_file
from .kawra_rpc import getnewaddress, listunspent, createrawtx, fundrawtx, signrawtx, sendrawtx

def mint_nft(blob: bytes, fname: str, owner_addr: str | None = None):
    cid = add_file(blob, fname)
    nft_id = uuid.uuid4().hex[:10]
    payload = f"{settings.NFT_TAG}{nft_id}|{cid}"
    if len(payload) > 80:
        raise ValueError("OP_RETURN too long")
    if not owner_addr:
        owner_addr = getnewaddress("nft-owner")
    utxo = next(u for u in listunspent() if u["amount"] > settings.NETWORK_FEE)
    ins = [{"txid": utxo["txid"], "vout": utxo["vout"]}]
    outs = {owner_addr: round(settings.DUST_AMOUNT,8), "data": payload.encode().hex()}
    tx = createrawtx(ins, outs)
    tx = fundrawtx(tx)
    tx = signrawtx(tx)
    txid = sendrawtx(tx)
    return {"txid": txid, "nft_id": nft_id, "cid": cid, "owner": owner_addr}

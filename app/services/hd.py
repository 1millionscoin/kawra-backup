import secrets
from bitcoinlib.keys import HDKey
from ..core.config import settings

def generate_seed():
    seed_bytes = secrets.token_bytes(32)
    hd = HDKey.from_seed(seed_bytes, network='bitcoin')  # Kawra shares Bitcoin params
    mnemonic = hd.mnemonic()
    xprv = hd.wif()
    xpub = hd.public().wif()
    return mnemonic, xprv, xpub

def derive_address(xpub: str, index: int):
    hd_pub = HDKey(xpub)
    child = hd_pub.subkey(index)
    return child.address()

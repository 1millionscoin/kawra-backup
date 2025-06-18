import itertools, requests
from ..core.config import settings

_counter = itertools.count()

def _rpc(method, *params):
    payload = {"jsonrpc":"1.0","id":next(_counter),"method":method,"params":list(params)}
    r = requests.post(settings.KAWRA_RPC_URL, json=payload,
                      auth=(settings.KAWRA_RPC_USER, settings.KAWRA_RPC_PASS), timeout=30)
    r.raise_for_status()
    j = r.json()
    if j.get("error"):
        raise RuntimeError(j["error"])
    return j["result"]

getnewaddress = lambda label="": _rpc("getnewaddress", label)
listunspent   = lambda minconf=1: _rpc("listunspent", minconf)
createrawtx   = lambda ins, outs: _rpc("createrawtransaction", ins, outs)
fundrawtx     = lambda h: _rpc("fundrawtransaction", h)["hex"]
signrawtx     = lambda h: _rpc("signrawtransactionwithwallet", h)["hex"]
sendrawtx     = lambda h: _rpc("sendrawtransaction", h)

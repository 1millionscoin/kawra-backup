import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routes import auth, assets, orders, nfts, pools, wallet, psbt
from .services import deposit_watcher, order_matcher, backup_uploader

app = FastAPI(title="Kawra DEX", version="1.0")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # adjust in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(auth.router)
app.include_router(assets.router)
app.include_router(orders.router)
app.include_router(nfts.router)
app.include_router(pools.router)
app.include_router(wallet.router)
app.include_router(psbt.router)

@app.on_event("startup")
async def startup():
    asyncio.create_task(deposit_watcher.credit_loop())
    asyncio.create_task(order_matcher.match_loop())
    asyncio.create_task(backup_uploader.backup_loop())

@app.get("/", include_in_schema=False)
def root():
    return {"status":"ok"}
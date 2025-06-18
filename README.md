# Kawra DEX / NFT Marketplace Backend

Spin‑up instructions:

```bash
git clone <repo>
cd kawra_dex
cp .env.example .env   # edit JWT_SECRET etc.
docker compose up -d --build
docker compose run --rm api python scripts/init_db.py
```

Then open http://localhost:8000/docs.

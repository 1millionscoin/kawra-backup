import os
from dotenv import load_dotenv
load_dotenv()

class Settings:
    KAWRA_RPC_URL  = os.getenv("KAWRA_RPC_URL")
    KAWRA_RPC_USER = os.getenv("KAWRA_RPC_USER")
    KAWRA_RPC_PASS = os.getenv("KAWRA_RPC_PASS")

    IPFS_API_URL   = os.getenv("IPFS_API_URL", "http://ipfs:5001")

    DB_BACKEND     = os.getenv("DB_BACKEND", "postgres")  # postgres | mongo
    POSTGRES_DSN   = os.getenv("POSTGRES_DSN")
    MONGO_DSN      = os.getenv("MONGO_DSN")

    JWT_SECRET     = os.getenv("JWT_SECRET")
    JWT_EXP_MIN    = 60*24*7

    NETWORK_FEE    = float(os.getenv("NETWORK_FEE", "0.0001"))
    DUST_AMOUNT    = float(os.getenv("DUST_AMOUNT", "0.00001"))

    NFT_TAG        = "KA1N|"
    TOKEN_TAG      = "KA1T|"
    LOCK_TAG       = "KA1L|"

settings = Settings()

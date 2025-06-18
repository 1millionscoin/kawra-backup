from .config import settings

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()

if settings.DB_BACKEND == "postgres":
    engine = create_async_engine(settings.POSTGRES_DSN, future=True, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

elif settings.DB_BACKEND == "sqlite":
    engine = create_async_engine("sqlite+aiosqlite:///./db.sqlite3", future=True, echo=False)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

elif settings.DB_BACKEND == "mongo":
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(settings.MONGO_DSN)
    db = client["kawra"]
    engine = None
    SessionLocal = None

else:
    raise ValueError("Unsupported DB_BACKEND")

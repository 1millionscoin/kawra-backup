from sqlalchemy import Column, Integer, String, Numeric, DateTime, Boolean, func
from ..core.db import Base

class Pool(Base):
    __tablename__ = "pools"
    id            = Column(Integer, primary_key=True)
    token_id      = Column(String(128), unique=True, nullable=False)
    reserve_kawra = Column(Numeric(38, 8), nullable=False)
    reserve_token = Column(Numeric(38, 8), nullable=False)
    tx_lock       = Column(String(64), nullable=False)
    locked        = Column(Boolean, default=True)
    created_at    = Column(DateTime, server_default=func.now())

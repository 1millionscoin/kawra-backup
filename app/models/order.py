from sqlalchemy import Column, Integer, Numeric, String, Boolean, DateTime, func
from ..core.db import Base

class Order(Base):
    __tablename__ = "orders"
    id        = Column(Integer, primary_key=True)
    user_id   = Column(Integer, index=True)
    side      = Column(String(4))
    base_id   = Column(String(128))
    quote_id  = Column(String(128))
    price     = Column(Numeric(38, 8))
    qty       = Column(Numeric(38, 8))
    filled    = Column(Numeric(38, 8), default=0)
    open      = Column(Boolean, default=True)
    placed_at = Column(DateTime, server_default=func.now())

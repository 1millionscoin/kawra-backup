from sqlalchemy import Column, Integer, String, Numeric, DateTime, func, Boolean
from ..core.db import Base

class NFTListing(Base):
    __tablename__ = "nft_listings"
    id        = Column(Integer, primary_key=True)
    nft_id    = Column(String(64), unique=True)
    owner_id  = Column(Integer)
    price     = Column(Numeric(38, 8))
    active    = Column(Boolean, default=True)
    listed_at = Column(DateTime, server_default=func.now())

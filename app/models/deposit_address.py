from sqlalchemy import Column, Integer, String, ForeignKey
from ..core.db import Base

class DepositAddress(Base):
    __tablename__ = "deposit_addresses"
    id        = Column(Integer, primary_key=True)
    user_id   = Column(Integer, ForeignKey("users.id"), index=True)
    address   = Column(String(64), unique=True, nullable=False)
    hd_index  = Column(Integer, nullable=False)

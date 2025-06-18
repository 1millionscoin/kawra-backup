from sqlalchemy import Column, Integer, String, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from ..core.db import Base

class Balance(Base):
    __tablename__ = "balances"
    id       = Column(Integer, primary_key=True)
    user_id  = Column(Integer, ForeignKey("users.id"))
    asset_id = Column(String(128), index=True)
    amount   = Column(Numeric(38, 8), default=0)

    owner = relationship("User", back_populates="balances")

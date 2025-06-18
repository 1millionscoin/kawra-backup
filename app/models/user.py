from sqlalchemy import Column, Integer, String, DateTime, func
from sqlalchemy.orm import relationship
from ..core.db import Base

class User(Base):
    __tablename__ = "users"
    id       = Column(Integer, primary_key=True)
    email    = Column(String(120), unique=True, nullable=False)
    pw_hash  = Column(String(128), nullable=False)
    xpub     = Column(String(256), unique=True, nullable=False)
    next_index = Column(Integer, default=0)
    created  = Column(DateTime, server_default=func.now())

    balances = relationship("Balance", back_populates="owner", cascade="all, delete-orphan")

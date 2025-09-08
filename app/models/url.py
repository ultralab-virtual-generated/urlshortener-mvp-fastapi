from sqlalchemy import Column, String, Integer, DateTime, func
from .db import Base


class URL(Base):
    __tablename__ = "urls"

    code = Column(String(16), primary_key=True, index=True)
    long_url = Column(String(2048), nullable=False)
    clicks = Column(Integer, nullable=False, default=0)
    last_clicked = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

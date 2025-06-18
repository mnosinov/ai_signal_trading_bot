from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()


class TradeSignal(Base):
    __tablename__ = "trade_signals"

    id = Column(Integer, primary_key=True)
    symbol = Column(String(20))
    signal_type = Column(String(10))  # BUY/SELL
    price = Column(Float)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    tp_price = Column(Float)
    sl_price = Column(Float)
    status = Column(String(20))  # OPEN/CLOSED

from sqlalchemy import Column, Integer, String, Numeric, Index
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class TickerPrice(Base):
    __tablename__ = "ticker_prices"

    id = Column(Integer, primary_key=True, index=True)
    ticker = Column(String, index=True)
    price = Column(Numeric(12, 8))
    timestamp = Column(Integer)

    __table_args__ = (
        Index('ix_ticker_timestamp', 'ticker', 'timestamp'),
    )
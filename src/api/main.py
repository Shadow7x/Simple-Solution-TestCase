import os

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from load_dotenv import load_dotenv
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from src.models import Base, TickerPrice
from src.schemas import PriceRecord, PricesResponse

load_dotenv()

app = FastAPI(title="Deribit Price API")


db_url = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:admin@db:5432/mydb")
engine = create_engine(db_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/prices/{ticker}", response_model=PricesResponse)
def get_prices(
    ticker: str = Path(..., description="Ticker symbol, e.g., btc_usd"),
    db: Session = Depends(get_db),
):
    stmt = select(TickerPrice).where(TickerPrice.ticker == ticker)
    results = db.execute(stmt).scalars().all()
    if not results:
        raise HTTPException(status_code=404, detail="No data found for ticker")
    return PricesResponse(data=results)


@app.get("/prices/latest/{ticker}", response_model=PriceRecord)
def get_latest_price(
    ticker: str = Path(..., description="Ticker symbol"), db: Session = Depends(get_db)
):
    stmt = (
        select(TickerPrice)
        .where(TickerPrice.ticker == ticker)
        .order_by(TickerPrice.timestamp.desc())
        .limit(1)
    )
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="No data found for ticker")
    return PriceRecord(**result.__dict__)


@app.get("/prices/history/{ticker}", response_model=PricesResponse)
def get_price_history(
    ticker: str = Path(..., description="Ticker symbol"),
    date: str = Query(..., description="Date in YYYY-MM-DD format"),
    db: Session = Depends(get_db),
):
    from datetime import datetime

    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    start_ts = int(datetime.combine(date_obj, datetime.min.time()).timestamp())
    end_ts = int(datetime.combine(date_obj, datetime.max.time()).timestamp())
    stmt = select(TickerPrice).where(
        TickerPrice.ticker == ticker, TickerPrice.timestamp.between(start_ts, end_ts)
    )
    results = db.execute(stmt).scalars().all()
    return PricesResponse(data=results)

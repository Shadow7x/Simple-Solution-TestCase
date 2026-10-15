from fastapi import FastAPI, Depends, HTTPException, Query
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.orm import declarative_base
from . import models, schemas

app = FastAPI(title="Deribit Price API")

# Database setup
engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/mydb")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/prices/{ticker}", response_model=schemas.PricesResponse)
def get_prices(ticker: str = Query(..., description="Ticker symbol, e.g., btc_usd"), db: Session = Depends(get_db)):
    stmt = select(models.TickerPrice).where(models.TickerPrice.ticker == ticker)
    results = db.execute(stmt).scalars().all()
    if not results:
        raise HTTPException(status_code=404, detail="No data found for ticker")
    return schemas.PricesResponse(data=results)

@app.get("/prices/latest/{ticker}", response_model=schemas.PriceRecord)
def get_latest_price(ticker: str = Query(..., description="Ticker symbol"), db: Session = Depends(get_db)):
    stmt = select(models.TickerPrice).where(models.TickerPrice.ticker == ticker).order_by(models.TickerPrice.timestamp.desc()).limit(1)
    result = db.execute(stmt).scalar_one_or_none()
    if result is None:
        raise HTTPException(status_code=404, detail="No data found for ticker")
    return schemas.PriceRecord(**result.__dict__)

@app.get("/prices/history/{ticker}", response_model=schemas.PricesResponse)
def get_price_history(ticker: str = Query(..., description="Ticker symbol"), date: str = Query(..., description="Date in YYYY-MM-DD format"), db: Session = Depends(get_db)):
    from datetime import datetime
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format")
    start_ts = int(datetime.combine(date_obj, datetime.min.time()).timestamp())
    end_ts = int(datetime.combine(date_obj, datetime.max.time()).timestamp())
    stmt = select(models.TickerPrice).where(models.TickerPrice.ticker == ticker, models.TickerPrice.timestamp.between(start_ts, end_ts))
    results = db.execute(stmt).scalars().all()
    return schemas.PricesResponse(data=results)
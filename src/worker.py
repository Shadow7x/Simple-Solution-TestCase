import asyncio
import os

import aiohttp
from celery import Celery
from load_dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models
from .client import fetch_price

load_dotenv()


celery_app = Celery(
    "worker",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)


engine = create_engine(
    os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:admin@db:5432/mydb")
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@celery_app.task
def fetch_and_save(ticker: str):
    async def _async_fetch():
        async with aiohttp.ClientSession() as session:
            price, timestamp = await fetch_price(session, ticker)
            db = SessionLocal()
            db.add(
                models.TickerPrice(
                    ticker=ticker, price=price, timestamp=int(timestamp.timestamp())
                )
            )
            db.commit()
            db.close()

    asyncio.run(_async_fetch())


celery_app.conf.beat_schedule = {
    "fetch-btc-price-every-minute": {
        "task": "src.worker.fetch_and_save",
        "schedule": 60.0,
        "args": ("btc_usd",),
    },
    "fetch-eth-price-every-minute": {
        "task": "src.worker.fetch_and_save",
        "schedule": 60.0,
        "args": ("eth_usd",),
    },
}

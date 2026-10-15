import os
from celery import Celery
import aiohttp
import asyncio
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from . import models, schemas

# Celery app configuration
celery_app = Celery('worker',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/0'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/0')
)

# Database engine for the worker (same as API)
engine = create_engine("postgresql+psycopg2://user:password@localhost:5432/mydb")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@celery_app.task
def fetch_and_save(ticker: str):
    async def _async_fetch():
        async with aiohttp.ClientSession() as session:
            price, timestamp = await fetch_price(session, ticker)
            db = SessionLocal()
            db.add(models.TickerPrice(ticker=ticker, price=price, timestamp=timestamp))
            db.commit()
            db.close()

    asyncio.run(_async_fetch())
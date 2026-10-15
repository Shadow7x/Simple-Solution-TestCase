import aiohttp
import asyncio
import time

async def fetch_price(session: aiohttp.ClientSession, ticker: str) -> tuple[float, int]:
    url = f"https://api.deribit.com/deribitapi/v2/public/price_index?symbol={ticker}"
    async with session.get(url) as response:
        data = await response.json()
        price = float(data['index_price'])
        timestamp = int(time.time())
        return price, timestamp
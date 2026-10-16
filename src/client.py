from datetime import UTC, datetime

import aiohttp

BASE_URL = "https://www.deribit.com/api/v2"

SUPPORTED_TICKERS = {
    "btc_usd",
    "eth_usd",
}


async def fetch_price(
    session: aiohttp.ClientSession,
    ticker: str,
) -> tuple[float, datetime]:
    ticker = ticker.lower()

    if ticker not in SUPPORTED_TICKERS:
        raise ValueError(f"Unsupported ticker: {ticker}")

    url = f"{BASE_URL}/public/get_index_price"

    params = {
        "index_name": ticker,
    }

    async with session.get(url, params=params) as response:
        response.raise_for_status()
        payload = await response.json()

    if "error" in payload:
        raise RuntimeError(f"Deribit API error: {payload['error']}")

    result = payload.get("result")

    if not isinstance(result, dict) or "index_price" not in result:
        raise ValueError(f"Unexpected Deribit response: {payload}")

    price = float(result["index_price"])

    timestamp = datetime.now(UTC)

    return price, timestamp

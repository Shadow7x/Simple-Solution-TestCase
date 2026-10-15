from pydantic import BaseModel
from typing import List

class PriceRecord(BaseModel):
    id: int
    ticker: str
    price: float
    timestamp: int

    class Config:
        orm_mode = True

class PricesResponse(BaseModel):
    data: List[PriceRecord]
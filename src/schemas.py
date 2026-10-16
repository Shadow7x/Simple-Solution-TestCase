from pydantic import BaseModel, ConfigDict


class PriceRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    ticker: str
    price: float
    timestamp: int


class PricesResponse(BaseModel):
    data: list[PriceRecord]

from pydantic import BaseModel


class Pair(BaseModel):
    symbol: str
    base_coin: str
    quote_coin: str
    last_price: float
    price_24h_percent: float
    volume_24h: float
    open_interest_1d: float | None
    buy_ratio: float | None
    funding: float | None


class Stats(BaseModel):
    reqs_1h: int
    reqs_1d: int
    reqs_7d: int


class Error(BaseModel):
    error: str
    msg: str

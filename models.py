from pydantic import BaseModel, Field


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


class UserRequest(BaseModel):
    quote_coin: str | None = None
    min_price: float | None = None
    max_price: float | None = None
    min_24h_percent: int | None = None
    max_24h_percent: int | None = None
    min_buy_ratio: float | None = None
    max_buy_ratio: float | None = None
    min_1d_open_interest: float | None = None
    max_1d_open_interest: float | None = None
    positive_funding: bool | None = None


class Stats(BaseModel):
    reqs_1h: int
    reqs_1d: int
    reqs_7d: int


class Error(BaseModel):
    error: str
    msg: str

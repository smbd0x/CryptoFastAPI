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


class UserRequest(BaseModel):
    quote_coin: str = 'USDT',
    min_price: float = 0,
    max_price: float = 1000000000000000,
    min_24h_percent: int = -1000000000000000,
    max_24h_percent: int = 1000000000000000,
    min_buy_ratio: float = 0,
    max_buy_ratio: float = 1,
    min_1d_open_interest: float = 0,
    max_1d_open_interest: float = 1000000000000000,
    positive_funding: bool | None = None,


class Stats(BaseModel):
    reqs_1h: int
    reqs_1d: int
    reqs_7d: int


class Error(BaseModel):
    error: str
    msg: str

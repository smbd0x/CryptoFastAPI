import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from config import TOP_30_CMC_COINS
from models import Error, Pair, Stats
from utils import (add_req_to_history, get_buy_ratios, get_coin_list,
                   get_funding_rates, get_open_interest_info, get_stats)

app = FastAPI()


@app.get('/stats')
async def get_stats_endpoint() -> Stats:
    stats = await get_stats()
    return stats


@app.get('/pairs', responses={'430': {'model': Error}})
async def get_pairs_endpoint(
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
) -> list[Pair]:
    await add_req_to_history(time.time(), quote_coin, min_price,
                             max_price, min_24h_percent, max_24h_percent, min_buy_ratio, max_buy_ratio,
                             min_1d_open_interest, max_1d_open_interest, positive_funding)

    r = await get_coin_list()
    if r.status_code == 200:
        coin_list = r.json()['result']['list']
        coin_list = [coin for coin in coin_list if coin['symbol']
                     in TOP_30_CMC_COINS]

        # Получении данных об открытом интересе для каждого инструмента
        open_interest = await get_open_interest_info(coin_list)

        # Получении данных о соотношении long/short для каждого инструмента
        buy_ratios = await get_buy_ratios(coin_list)

        # Получении данных о фандинге для каждого инструмента
        funding_rates = await get_funding_rates(coin_list)

        # Формирование списка с результатами
        result = [
            {
                'symbol': coin['symbol'],
                'base_coin': coin['symbol'][:-4],
                'quote_coin': 'USDT',
                'last_price': coin['lastPrice'],
                'price_24h_percent': float(coin['price24hPcnt']) * 100,
                'volume_24h': float(coin['volume24h']),
                'open_interest_1d': float(open_interest[coin['symbol']]),
                'buy_ratio': float(buy_ratios[coin['symbol']]),
                'funding': float(funding_rates[coin['symbol']]),
            } for coin in coin_list if (open_interest.get(coin['symbol']) and buy_ratios.get(
                coin['symbol']) and funding_rates.get(coin['symbol'])) and (min_price <= float(coin[
                    'lastPrice']) <= max_price and min_24h_percent <= float(
                    coin['price24hPcnt']) * 100 <= max_24h_percent and min_buy_ratio <=
                    float(buy_ratios[coin['symbol']]) <= max_buy_ratio and min_1d_open_interest <=
                    float(open_interest[coin['symbol']]) <= max_1d_open_interest and quote_coin ==
                    coin['symbol'][-4:]) and (
                    (positive_funding and float(funding_rates[coin['symbol']]) >= 0) or (
                        positive_funding is False and float(funding_rates[coin['symbol']]) <= 0) or (
                        positive_funding is None))
        ]

        return result
    else:
        return JSONResponse(status_code=430, content={'error': 'Bybit API Error', 'msg': r.reason_phrase})

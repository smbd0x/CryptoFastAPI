import asyncio

import redis
import time

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from config import TOP_30_CMC_COINS
from models import Error, Pair, Stats
from utils import (add_req_to_history, get_buy_ratios, get_coin_list,
                   get_funding_rates, get_open_interest_info, get_stats, get_redis_timestamp, get_cache, set_cache,
                   check_filter)

app = FastAPI()
redis_client = redis.Redis(host='redis', port=6379)


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

    # Проверка актуальности кэша
    redis_timestamp = get_redis_timestamp(redis_client)
    if time.time() - 5 <= redis_timestamp:
        all_coins = get_cache(redis_client)
    else:
        r = await get_coin_list()
        if r.status_code == 200:
            coin_list = r.json()['result']['list']
            coin_list = [coin for coin in coin_list if coin['symbol']
                         in TOP_30_CMC_COINS]

            # Получении данных об открытом интересе, соотношении long/short для каждого инструмента
            open_interest, buy_ratios, funding_rates = await asyncio.gather(get_open_interest_info(coin_list),
                                                                            get_buy_ratios(coin_list),
                                                                            get_funding_rates(coin_list))

            # Формирование списка со всеми монетами
            all_coins = [
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
                    coin['symbol']) and funding_rates.get(coin['symbol']))
            ]

            set_cache(redis_client, all_coins)

        else:
            return JSONResponse(status_code=430, content={'error': 'Bybit API Error', 'msg': r.reason_phrase})

    # Формирование списка с результатами (фильтрация монет)
    result = [coin_info for coin_info in all_coins if check_filter(coin_info, quote_coin, min_price,
                                                                   max_price, min_24h_percent, max_24h_percent,
                                                                   min_buy_ratio, max_buy_ratio,
                                                                   min_1d_open_interest, max_1d_open_interest,
                                                                   positive_funding)]

    return result

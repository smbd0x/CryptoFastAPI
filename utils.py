import asyncio
import json

import time

import pandas as pd
from httpx import AsyncClient, Response
from redis import Redis

from config import BYBIT_API_URL
from models import UserRequest


async def multiple_http_request(client: AsyncClient, url: str, params: list[dict]) -> tuple:
    """Выполняет несколько http запросов асинхронно."""
    reqs = [client.get(url, params=p, timeout=100) for p in params]
    result = await asyncio.gather(*reqs)
    return result


async def add_req_to_history(*args):
    """Записывает аргументы в новую строку в файле history.csv."""
    with open('history.csv', 'a') as file:
        args = map(str, args)
        file.write(','.join(args) + '\n')


async def get_open_interest_info(coin_list: list[dict]) -> dict:
    """Возвращает словарь со значениями открытого интереса для монет из списка coin_list."""
    async with AsyncClient() as client:
        get_open_interest_url = f'{BYBIT_API_URL}/market/open-interest'
        open_interest = await multiple_http_request(client, get_open_interest_url,
                                                    [{'category': 'linear', 'symbol': coin['symbol'],
                                                      'intervalTime': '1d', 'limit': 1} for coin in
                                                     coin_list])
        open_interest = {i.json()['result']['symbol']: i.json()['result']['list'][0]['openInterest'] for
                         i in open_interest if i.json()['result'].get('list') if i.json()['result'].get('list')}
        return open_interest


async def get_buy_ratios(coin_list: list[dict]) -> dict:
    """Возвращает словарь с соотношениями long/short для монет из списка coin_list."""
    async with AsyncClient() as client:
        get_buy_ratio_url = f'{BYBIT_API_URL}/market/account-ratio'
        buy_ratios = await multiple_http_request(client, get_buy_ratio_url,
                                                 [{'category': 'linear', 'symbol': coin['symbol'], 'period': '1d',
                                                   'limit': 1} for
                                                  coin in
                                                  coin_list])
        buy_ratios = {i.json()['result']['list'][0]['symbol']: i.json()['result']['list'][0]['buyRatio'] for
                      i in buy_ratios if i.json()['result'].get('list')}
        return buy_ratios


async def get_funding_rates(coin_list: list[dict]) -> dict:
    """Возвращает словарь со значениями фандинга для монет из списка coin_list."""
    async with AsyncClient() as client:
        get_funding_url = f'{BYBIT_API_URL}/market/funding/history'
        funding_rates = await multiple_http_request(client, get_funding_url,
                                                    [{'category': 'linear', 'symbol': coin['symbol'], 'limit': 1}
                                                     for
                                                     coin in
                                                     coin_list])
        funding_rates = {i.json()['result']['list'][0]['symbol']: i.json()['result']['list'][0]['fundingRate'] for
                         i in funding_rates if i.json()['result'].get('list')}
        return funding_rates


async def get_coin_list() -> Response:
    """Возвращает Response со списком торговых пар с биржи Bybit."""
    async with AsyncClient() as client:
        get_tickers_url = f'{BYBIT_API_URL}/market/tickers'
        r = await client.get(get_tickers_url, params={'category': 'spot'})
        return r


async def get_stats() -> dict:
    """Возвращает словарь со статистикой из файла history.csv."""
    df = pd.read_csv('history.csv')
    df_1h = df[df['timestamp'] >= time.time() - 60 * 60]
    df_1d = df[df['timestamp'] >= time.time() - 60 * 60 * 24]
    df_7d = df[df['timestamp'] >= time.time() - 60 * 60 * 24 * 7]
    return {
        'reqs_1h': len(df_1h),
        'reqs_1d': len(df_1d),
        'reqs_7d': len(df_7d),
    }


def set_cache(redis_client: Redis, all_coins: list[dict]):
    """Добавляет список монет в кэш Redis."""
    redis_client.set('all_coins', json.dumps(all_coins))
    redis_client.set('timestamp', time.time())


def get_cache(redis_client: Redis) -> list[dict]:
    """Получает список монет из кэша Redis."""
    res = redis_client.get('all_coins')
    return json.loads(res.decode('utf-8'))


def get_redis_timestamp(redis_client: Redis) -> float:
    """Получает timestamp из кэша Redis."""
    res = redis_client.get('timestamp')
    if res:
        return float(res.decode('utf-8'))
    else:
        return 0


def check_filter(
        coin_info: dict,
        user_request: UserRequest,
) -> bool:
    """Проверят данные о монете на соответствие заданным фильтрам."""
    if user_request.min_price and user_request.min_price > float(coin_info['last_price']):
        return False
    if user_request.max_price and user_request.max_price < float(coin_info['last_price']):
        return False
    if user_request.min_24h_percent and user_request.min_24h_percent > float(coin_info['price_24h_percent']):
        return False
    if user_request.max_24h_percent and user_request.max_24h_percent < float(coin_info['price_24h_percent']):
        return False
    if user_request.min_buy_ratio and user_request.min_buy_ratio > float(coin_info['buy_ratio']):
        return False
    if user_request.max_buy_ratio and user_request.max_buy_ratio < float(coin_info['buy_ratio']):
        return False
    if user_request.min_1d_open_interest and user_request.min_1d_open_interest > float(coin_info['open_interest_1d']):
        return False
    if user_request.max_1d_open_interest and user_request.max_1d_open_interest < float(coin_info['open_interest_1d']):
        return False
    if user_request.quote_coin and user_request.quote_coin != coin_info['quote_coin']:
        return False
    if user_request.positive_funding and user_request.positive_funding != (
            True if float(coin_info['funding']) >= 0 else False):
        return False
    return True

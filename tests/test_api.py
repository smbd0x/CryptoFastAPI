import asyncio
import time

import pytest
from fastapi.testclient import TestClient
from main import app, redis_client
from httpx import ASGITransport, AsyncClient

client = TestClient(app)


def test_send_req():
    response = client.get('/pairs')
    assert response.status_code == 200


def test_speed_without_cache():
    times = []
    for i in range(10):
        t1 = time.time()
        response = client.get('/pairs')
        t2 = time.time()
        assert response.status_code == 200
        times.append(t2-t1)
        time.sleep(5.1)
    print(f'Среднее время выполнения запроса без кэша (10 запросов): {sum(times)/len(times)}s')


def test_speed_with_cache():
    times = []
    for i in range(30):
        t1 = time.time()
        response = client.get('/pairs')
        t2 = time.time()
        assert response.status_code == 200
        times.append(t2-t1)
        time.sleep(1)
    print(f'Среднее время выполнения запроса с кэшем (30 запросов): {sum(times)/len(times)}s')


@pytest.mark.asyncio
async def test_100_reqs_async():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        reqs = [ac.get('/pairs') for _ in range(100)]
        t1 = time.time()
        responses = await asyncio.gather(*reqs)
        t2 = time.time()
        for resp in responses:
            assert resp.status_code == 200
        print(f'Время выполнения 100 запросов асинхронно: {t2-t1}s')


@pytest.mark.asyncio
async def test_500_reqs_async():
    async with AsyncClient(
            transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        reqs = [ac.get('/pairs') for _ in range(500)]
        t1 = time.time()
        responses = await asyncio.gather(*reqs)
        t2 = time.time()
        for resp in responses:
            assert resp.status_code == 200
        print(f'Время выполнения 500 запросов асинхронно: {t2-t1}s')

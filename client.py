from typing import Coroutine
import aiohttp
import asyncio
import time
import httpx

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.text()
    pass

async def fetchSite():
    url = "https://www.example.com"
    content = await fetch(url)
    print("Content is done")

def timeit(func: Coroutine):
    # decorator
    async def wrapper(*args, **kwargs):
        start = time.time()
        print("Timing started")
        await func(*args, **kwargs)
        print(f"Time taken: {time.time() - start}")
    return wrapper

@timeit
async def async_get_request(url, params=None, headers=None):
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params, headers=headers, timeout=300)
        return response

@timeit
async def async_post_request(url, data=None, json=None, headers=None):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, data=data, json=json, headers=headers)
        return response

async def test_concurrent(concur_num, url):
    tasks = []
    for _ in range(concur_num):
        tasks.append(asyncio.create_task(async_get_request(url)))
    await asyncio.gather(*tasks)
    print("Done")

async def main():
    concur_num = 16
    # await test_sync_sleep(concur_num)
    print(f"TASK: sleep for 3 secs and return. {concur_num} tasks will be run concurrently.")

    print("Sync (basic) request, worker=4")
    await test_concurrent(concur_num, "http://localhost:8005/sync_sleep")
    print("-------------------")

    print("sync requests, but they have been asynchronized to join the uvicorn event loop")
    await test_concurrent(concur_num, "http://localhost:8005/async_sleep")
    print("-------------------")

    # print(f"TASK: calculate fib(100000) and return result. {concur_num} tasks will be run concurrently.")

    # print("Sync (basic) request, worker=4")
    # await test_concurrent(concur_num, "http://localhost:8005/sync_fib")
    # print("-------------------")

    # print("sync requests, but they have been asynchronized to join the uvicorn event loop")
    # await test_concurrent(concur_num, "http://localhost:8005/async_fib")
    # print("-------------------")

    print(f"TASK: fetch examples.com 10 times. {concur_num} tasks will be run concurrently.")

    print("Sync (basic) request, worker=4")
    await test_concurrent(concur_num, "http://localhost:8005/bad_op_fetch")
    print("-------------------")

    print("sync requests, but they have been asynchronized to join the uvicorn event loop")
    # How it works: uvicorn event loop listens to fd via `selector`
    await test_concurrent(concur_num, "http://localhost:8005/async_bad_op")


if __name__ == "__main__":
    asyncio.run(main())

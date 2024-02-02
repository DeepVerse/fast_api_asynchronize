import asyncio
from typing import Callable
import fastapi
from fastapi.responses import StreamingResponse
import uvicorn
import time
import requests

app = fastapi.FastAPI()

# @app.get("/test")
# async def sleep_test():
#     time.sleep(3)
#     return "ok"

# @app.get("/async_test")
# async def async_sleep_test():
#     await asyncio.sleep(3)
#     return "ok"

def bad_op_sleep() -> None:
    """
        emulates an IO procedure
        which doesn't support native async/await, will block current thread
    """
    time.sleep(3)
    return "ok"

def bad_op_fib() -> int:
    """
        emulates an CPU-bound procedure
        which doesn't support native async/await, will occupy current thread
    """
    def fib(n) -> int:
        if n <= 2:
            return 1
        return fib(n - 1) + fib(n - 2)
    return fib(100000)

def bad_op_fetch(url) -> str:
    """
        time-consuming IO op
    """
    def sync_fetch(url):
        try:
            # send HTTP request
            response = requests.get(url)

            # check if success (status 200)
            if response.status_code == 200:
                return response.text
            else:
                print(f"Request failed, status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None

    # fetch example.com 10 times and concat the first & last char of every fetch
    show_me_result = ""
    for _ in range(10):
        resp = sync_fetch(url)
        show_me_result += resp[0] + resp[len(resp) - 1]

    return f"First chat: {show_me_result[0]}"

################################
# convert sync task to async
################################
async def make_sync_async(sync_f, *args, **kwargs):
    loop = asyncio.get_running_loop()  # merge params and func into a nonparam func closure
    f: Callable = lambda: sync_f(*args, **kwargs)
    return await loop.run_in_executor(None, f)

################################
#  Basically, make_sync_async == run_in_threadpool
################################
@app.get("/sync_fib")
def sync_fib():
    return bad_op_fib()

@app.get("/async_fib")
async def async_fib():
    return await make_sync_async(bad_op_fib)

@app.get("/sync_sleep")
def sync_sleep():
    bad_op_sleep()
    return "ok"

@app.get("/async_sleep")
async def async_sleep():
    await make_sync_async(bad_op_sleep)
    return "ok"

@app.get("/bad_op_fetch")
async def bad_op_fecth():
    url = "https://www.example.com"
    return bad_op_fetch(url)

from fastapi.concurrency import run_in_threadpool

@app.get("/async_bad_op")
async def good_op_fecth():
    url = "https://www.example.com"
    return await run_in_threadpool(bad_op_fetch, url)

"""
    ------------------------------
"""

# import openai

# question = ""

# @app.post("/sync_chat")
# def chat_sync():
#     completion = openai.ChatCompletion.create(
#         stream=True,
#         messages=[{"text": question, "role": "user"}]
#     )
#     return StreamingResponse(
#         completion,
#         media_type="application/octet-stream",
#     )

# @app.post("/async_chat")
# async def async_chat():
#     completion = await openai.ChatCompletion.acreate(
#         stream=True,
#         messages=[{"text": question, "role": "user"}]
#     )
#     return StreamingResponse(
#         completion,
#         media_type="application/octet-stream",
#     )

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8005,
        log_level="info",
        workers=4,
    )

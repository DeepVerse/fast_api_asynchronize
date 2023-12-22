import asyncio
from typing import Callable
import fastapi
import uvicorn
import time
import requests

app = fastapi.FastAPI()

@app.get("/test")
async def sleep_test():
    time.sleep(3)
    return "ok"

@app.get("/async_test")
async def async_sleep_test():
    await asyncio.sleep(3)
    return "ok"


def bad_op_sleep():
    """
        emulates an IO procedure
        which doesn't support native async/await, will block current thread
    """
    time.sleep(3)
    return "ok"

def bad_op_fetch(url):
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
                print(f"Request failed，status code: {response.status_code}")
                return None
        except Exception as e:
            print(f"Exception: {e}")
            return None

    # fetch example.com 10 times and concat the first & last char of every fetch
    show_me_result = ""
    for _ in range(5):
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
#
################################

@app.get("/sync_to_async")
async def convert():
    return await make_sync_async(bad_op_sleep)

@app.get("/bad_op_fetch")
async def bad_op_fecth():
    url = "https://www.example.com"
    return bad_op_fetch(url)

from fastapi.concurrency import run_in_threadpool

@app.get("/async_bad_op")
async def good_op_fecth():
    url = "https://www.example.com"
    return await run_in_threadpool(bad_op_fetch, url)
    # return await make_sync_async(bad_op_fetch, url)

if __name__ == "__main__":
    uvicorn.run(
        "server:app",
        host="127.0.0.1",
        port=8005,
        log_level="info",
        workers=4,
    )

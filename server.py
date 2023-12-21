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
        模拟了一个耗时的IO操作
        底层不支持异步IO, 会阻塞整个进程
    """
    time.sleep(3)
    return "ok"

def bad_op_fetch(url):
    """
        耗时的IO操作
    """
    def sync_fetch(url):
        try:
            # 发送 HTTP 请求
            response = requests.get(url)

            # 检查请求是否成功 (状态码为 200)
            if response.status_code == 200:
                # 返回网页内容
                return response.text
            else:
                print(f"请求失败，状态码: {response.status_code}")
                return None
        except Exception as e:
            print(f"发生异常: {e}")
            return None

    # fetch example.com 10 times and concat the first & last char of every fetch
    show_me_result = ""
    for _ in range(5):
        resp = sync_fetch(url)
        show_me_result += resp[0] + resp[len(resp) - 1]

    return f"First chat: {show_me_result[0]}"

################################
# 将同步任务转换为异步任务的代码
################################

async def make_sync_async(sync_f, *args, **kwargs):
    loop = asyncio.get_running_loop()  # 将函数和参数合并成一个无参数的闭包
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

"""
    My implementation of coroutine!
    Based on yield/yield from - generator
"""

from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
import socket
from typing import Generator

selector = DefaultSelector()

class Future:

    def __init__(self):
        self.result = None
        self.callbacks = []

    def add_done_callback(self, fn):
        self.callbacks.append(fn)

    def resolve(self):
        for fn in self.callbacks:
            fn()

class Task:
    def __init__(self, gen, eventLoop):
        self.gen = gen
        self.eventLoop = eventLoop
        self.step()

    def step(self):
        try:
            f = next(self.gen)
            f.callbacks.append(self.step)
        except StopIteration:
            self.eventLoop.n_task -= 1

class EventLoop:

    def __init__(self):
        self.n_task = 0

    def add_task(self, gen: Generator):
        self.n_task += 1
        Task(gen, self)

    def start(self):
        while self.n_task > 0:
            events = selector.select()
            for key, mask in events:
                f = key.data
                f.resolve()

def async_await(s: socket, event: int):
    f = Future()
    selector.register(s.fileno(), event, f)
    yield f
    selector.unregister(s.fileno())  # resume

def get(host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)

    try:
        sock.connect((host, 80))
    except BlockingIOError as e:
        print(e)

    yield from async_await(sock, EVENT_WRITE)
    req = f'GET / HTTP/1.1\r\nHost: {host}\r\n\r\n'
    sock.send(req.encode('ascii'))

    while True:
        yield from async_await(sock, EVENT_READ)

        received = sock.recv(4096)
        print(received)

def timeit():
    pass


if __name__ == "__main__":

    host = "www.example.com"

    el = EventLoop()
    el.add_task(get(host))
    # el.add_task(get(host))
    # el.add_task(get(host))  # add any number of tasks here and select io poll will happen
    el.start()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division



import time
from collections import deque
from tornado.concurrent import Future
from tornado import gen
from tornado.ioloop import IOLoop
from tornado.locks import Semaphore
from tornado.queues import Queue
import tornado.web


futures_q = deque([Future() for _ in range(3)])

@gen.coroutine
def simulator(futures):
   for f in futures:
       yield gen.moment
       f.set_result(None)

IOLoop.current().add_callback(simulator, list(futures_q))

def use_some_resource(worker_id, ret):
    ret.append(worker_id + 1)
    gen.sleep(1)
    print('1 coming')
    raise gen.Return(1)
#    return futures_q.popleft()

def get_other(worker_id, ret):
    ret.append(worker_id + 1)
    gen.sleep(1)
    print('0, 2 eat')
    raise gen.Return(0)

sem = Semaphore(10)

@gen.coroutine
def worker(worker_id, ret):
    with (yield sem.acquire()):
        print("Worker %d is working" % worker_id)
        if worker_id == 1:
            response = yield use_some_resource(worker_id, ret)
        else:
            response = (yield get_other(worker_id, ret))
        print(response)
        print("Worker %d is done" % worker_id)

@gen.coroutine
def runner(result):
    # Join all workers.
    yield [worker(i, result) for i in range(5)]

    time.sleep(2)
    print(result)



class MainHandler(tornado.web.RequestHandler):
    def get(self):
        result = []
        runner(result)
        print('result', result)
        self.write("Hello, world")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    IOLoop.current().start()


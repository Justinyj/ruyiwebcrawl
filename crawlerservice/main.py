#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from collections import deque

from tornado import gen
from tornado.concurrent import Future
from tornado.options import define, options

import tornado.ioloop
import tornado.httpserver

from urls import urls

from settings import CONCURRENT_NUM


define('port', default=8888, type=int, help='process port')
define('process', default=1, type=int, help='process number')
define('program', default='proxy', help='RESTFul program name')


def prepare_checkproxy():
    futures_q = deque([Future() for _ in range(CONCURRENT_NUM)])

    @gen.coroutine
    def simulator(futures):
        for f in futures:
            yield gen.moment
            f.set_result(None)

    tornado.ioloop.IOLoop.current().add_callback(simulator, list(futures_q))

if __name__ == "__main__":
    # python main.py -port=8000 -process=4 -program=cache
    # python main.py -program=proxy
    tornado.options.parse_command_line()

    http_server = tornado.httpserver.HTTPServer(urls, xheaders=True)
    http_server.bind(options.port)
    http_server.start(options.process)

    if options.program == 'proxy':
        prepare_checkproxy()

    tornado.ioloop.IOLoop.current().start()


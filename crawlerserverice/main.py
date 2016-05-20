#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from tornado.options import define, options
import tornado.ioloop
import tornado.httpserver

from urls import urls

define('port', default=8888, type=int, help='process port')
define('process', default=1, type=int, help='process number')


if __name__ == "__main__":
    # python main.py -port=8000 -process=8
    tornado.options.parse_command_line()

    http_server = tornado.httpserver.HTTPServer(urls, xheaders=True)
    http_server.bind(options.port)
    http_server.start(options.process)
    tornado.ioloop.IOLoop.current().start()


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from gevent import monkey; monkey.patch_all()
import gevent

import tornado.httpserver
import tornado.ioloop

from tornado.options import define, options

from router import urls
from stream_process import stream_process


define('port', default=8100, type=int, help='process port')
define('process', default=1, type=int, help='process number')

if __name__ == '__main__':
    tornado.options.parse_command_line()

    gevent.spawn(stream_process)

    http_server = tornado.httpserver.HTTPServer(urls, xheaders=True)
    http_server.bind(options.port)
    http_server.start(options.process)
    tornado.ioloop.IOLoop.current().start()


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import tornado.options
import tornado.ioloop
import tornado.httpserver

from urls import urls

PORT = 8888


if __name__ == "__main__":
    port = tornado.options.parse_command_line()
    port = port[0] if port and port[0] else PORT

    http_server = tornado.httpserver.HTTPServer(urls, xheaders=True)
    http_server.listen(int(port))
    tornado.ioloop.IOLoop.current().start()


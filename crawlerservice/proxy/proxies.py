#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division


MIMVIP_PROXIES = [
  {u'http_type': u'HTTP', u'ip:port': u'223.27.194.166:8080'},
  {u'http_type': u'HTTP', u'ip:port': u'182.72.113.114:3128'},
  {u'http_type': u'HTTPS', u'ip:port': u'202.173.214.15:8080'},
  {u'http_type': u'HTTP', u'ip:port': u'114.40.13.114:3128'},
  {u'http_type': u'HTTP/HTTPS', u'ip:port': u'61.5.22.6:3128'},
  {u'http_type': u'HTTPS', u'ip:port': u'103.20.89.25:8080'},
  {u'http_type': u'HTTP', u'ip:port': u'107.151.152.218:80'},
  {u'http_type': u'HTTP', u'ip:port': u'202.108.23.247:80'},
  {u'http_type': u'HTTP', u'ip:port': u'101.96.10.46:8088'},
  {u'http_type': u'HTTP/HTTPS', u'ip:port': u'45.32.59.161:3128'},
  {u'http_type': u'HTTP', u'ip:port': u'177.65.219.168:8080'},
  {u'http_type': u'HTTPS', u'ip:port': u'181.55.151.34:8080'},
  {u'http_type': u'HTTP/HTTPS', u'ip:port': u'190.82.94.13:80'},
  {u'http_type': u'HTTP', u'ip:port': u'218.3.230.2:3128'},
  {u'http_type': u'HTTP/HTTPS', u'ip:port': u'179.185.4.116:8080'},
  {u'http_type': u'HTTP', u'ip:port': u'101.96.11.30:8090'},
  {u'http_type': u'HTTP/HTTPS', u'ip:port': u'88.80.16.87:80'}
]

FREE_PROXIES = [
    {"ip_port": "181.48.0.173:8081"},
    {"ip_port": "82.43.21.165:3128"},
    {"ip_port": "185.112.234.4:80"},
    {"ip_port": "118.189.13.178:8080"},
    {"ip_port": "37.187.117.157:3128"},
    {"ip_port": "62.201.200.17:80"},
    {"ip_port": "181.143.28.210:3128"},
    {"ip_port": "216.190.97.3:3128"},
    {"ip_port": "183.111.169.205:3128"},
]


PROXIES = parse_proxies()

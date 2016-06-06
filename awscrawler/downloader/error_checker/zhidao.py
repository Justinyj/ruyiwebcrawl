#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

error_checker = lambda response: False if response.headers['Content-Type'] == 'text/html' else True

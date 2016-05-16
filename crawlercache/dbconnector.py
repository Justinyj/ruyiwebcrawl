#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from pgwrapper import PGWrapper
from settings import *

dbwrapper = PGWrapper(dbname=DBNAME,
                      user=DBUSER,
                      password=DBPASS,
                      host=DBHOST,
                      port=DBPORT)


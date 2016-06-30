#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re

regchinese = re.compile(u'^[\u4e00-\u9fff]+$')
regdisambiguation = re.compile(u'(.*)_\([^\)]+\)') # 101省道_(浙江)
regfdentitysearch = re.compile(u'(.+?)(\(|（).+(\)|）)')

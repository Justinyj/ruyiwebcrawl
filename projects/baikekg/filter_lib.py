#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
from functools import partial

regchinese = re.compile(u'^[\u4e00-\u9fff]+$')
regdisambiguation = re.compile(u'(.*)_\([^\)]+\)') # 101省道_(浙江)
regdropbrackets = re.compile(u'(.+?)(\(|（).+(\)|）)')

regrmlabel = partial(re.sub, '</?[A-Za-z]+>', '')
regentityfilt = re.compile(u'^《?([\u4e00-\u9fff·\-\ A-Za-z0-9]+)》?(\(|（)?[0-9,～\u4e00-\u9fff]*(\)|）)?$')

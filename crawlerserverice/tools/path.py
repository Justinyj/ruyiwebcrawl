#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import os

def makedir(absdir):
    if not os.path.exists(absdir):
        os.makedirs(absdir)

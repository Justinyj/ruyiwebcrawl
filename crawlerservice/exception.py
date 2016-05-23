#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

def exception(func):
    def exe_function(self, *args, **kwargs):
        try:
            func(self, *args, **kwargs)
        except Exception as e:
            self.write(str(e))

    return exe_function


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib

from awsapi.s3object import S3Object

class Fetcher(object):
    def __init__(self, batch_id, region_name='ap-northeast-1'):
        self.batch_id = batch_id
        self.batch_key = batch_id.rsplit('-', 1)[0]
        self.S3 = S3Object(batch_id, region_name)


    def fetch(self):
        pass


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import hashlib

from awsapi.s3object import S3Object


class CacheS3(object):

    def __init__(self, batch_id, region_name='ap-northeast-1'):
        self.batch_id = batch_id
        self.batch_key = batch_id.rsplit('-', 1)[0]
        self.S3 = S3Object(batch_id, region_name)


    def exists(self, url):
        url_hash = hashlib.sha1(url).hexdigest()
        filename = '{}_{}'.format(self.batch_id, url_hash)
        return self.S3.head_cache(filename)


    def get(self, url):
        try:
            url_hash = hashlib.sha1(url).hexdigest()
            filename = '{}_{}'.format(self.batch_id, url_hash)
            #check exists before get
            if not self.S3.head_cache(filename):
                return u''
            ret = self.S3.get_cache(filename)
            if 'error' in ret:
                return u''
        except Exception as e:
            return u''

        return ret['content']


    def post(self, url, content, groups=None, refresh=False):
        try:
            url_hash = hashlib.sha1(url).hexdigest()
            filename = '{}_{}'.format(self.batch_id, url_hash)
            ret = self.S3.put_cache(filename, content)
            if 'error' in ret and ret['error'] == 'NoSuchBucket':
                ret = self.S3.put_cache(filename, content)
            if 'error' in ret:
                return ret['error']
        except Exception as e:
            return e
        return True


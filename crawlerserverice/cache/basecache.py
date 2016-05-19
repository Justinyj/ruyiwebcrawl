#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import base64
import hashlib

from settings import CACHEPAGE
from .fscache import fs_get_cache, fs_set_cache
from .dbcache import db_get_cache, db_set_cache, db_get_all_cache
#from .qiniucache import *


class BaseCache(object):
    def __init__(self):
        pass

    @staticmethod
    def get_cache(b64url, batch_id):
        url = base64.urlsafe_b64decode(b64url)
        hashkey = hashlib.sha1(url).hexdigest()

        if CACHEPAGE == 'pg':
            return db_get_cache(hashkey)
        elif CACHEPAGE == 'qiniu':
            pass
        elif CACHEPAGE == 'fs':
            return fs_get_cache(b64url, batch_id)


    @staticmethod
    def set_cache(b64url, batch_id, groups, content, refresh):
        url = base64.urlsafe_b64decode(b64url)
        hashkey = hashlib.sha1(url).hexdigest()

        if CACHEPAGE == 'pg':
            return db_set_cache(hashkey, url, batch_id, content)
        elif CACHEPAGE == 'qiniu':
            pass
        elif CACHEPAGE == 'fs':
            return fs_set_cache(b64url, batch_id, groups, content, refresh)


    @staticmethod
    def get_all_cache(batch_id):
        if CACHEPAGE == 'pg':
            return db_get_all_cache(batch_id)


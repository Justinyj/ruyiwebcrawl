#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import base64
import hashlib

from settings import CACHEPAGE
from .fscache import fs_get_cache, fs_set_cache
from .dbcache import db_get_cache, db_set_cache, db_get_all_cache
from .ufilecache import ufile_get_cache, ufile_set_cache
#from .qiniucache import *


class BaseCache(object):
    def __init__(self):
        pass

    @staticmethod
    def get_cache(b64url, batch_id):
        url = base64.urlsafe_b64decode(b64url)
        url_hash = hashlib.sha1(url).hexdigest()

        if CACHEPAGE == 'pg':
            return db_get_cache(url_hash)
        elif CACHEPAGE == 'qiniu':
            pass
        elif CACHEPAGE == 'fs':
            return fs_get_cache(b64url, url_hash, batch_id)
        elif CACHEPAGE == 'ufile':
            return ufile_get_cache(batch_id, url_hash)


    @staticmethod
    def set_cache(b64url, batch_id, groups, content, refresh):
        url = base64.urlsafe_b64decode(b64url)
        url_hash = hashlib.sha1(url).hexdigest()

        if CACHEPAGE == 'pg':
            return db_set_cache(b64url, url_hash, batch_id, groups, content, refresh)
        elif CACHEPAGE == 'qiniu':
            pass
        elif CACHEPAGE == 'fs':
            return fs_set_cache(b64url, url_hash, batch_id, groups, content, refresh)
        elif CACHEPAGE == 'ufile':
            return ufile_set_cache(b64url, url_hash, batch_id, groups, content, refresh)


    @staticmethod
    def get_all_cache(batch_id):
        if CACHEPAGE == 'pg':
            return db_get_all_cache(batch_id)


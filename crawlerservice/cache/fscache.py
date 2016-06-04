#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
#
# 1. directory hierarchy: raw/{lastest, snapshot(url+date)}, meta/*.log.
#    purpose: if URL is deleted by website.
# 2. log name: ip+date.log
#    purpose: tornado setup on different machine, rsync log merge.
# 3. log content: date, batch_id, group, URL, remote_ip.

from __future__ import print_function, division
from datetime import datetime

import base64
import hashlib
import json
import os

from settings import FSCACHEDIR
from tools import path, cachelog


def fs_get_cache(b64url, url_hash, batch_id):
    try:
        assert len(batch_id) > 0
        level1 = url_hash[0]
        level2 = url_hash[-2:]

        absdir = os.path.join(FSCACHEDIR, batch_id, 'raw', 'latest', level1, level2)
        cache_file = os.path.join(absdir, url_hash)
        if os.path.isfile(cache_file):
            with open(cache_file) as fd:
                html = fd.read()
        else:
            return {'success': False}
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True, 'content': html}


def fs_set_cache(b64url, url_hash, batch_id, groups, content, refresh=False):
    try:
        assert len(batch_id) > 0
        level1 = url_hash[0]
        level2 = url_hash[-2:]

        absdir = os.path.join(FSCACHEDIR, batch_id, 'raw', 'latest', level1, level2)
        cache_file = os.path.join(absdir, url_hash)

        path.makedir(absdir)
        if refresh or not os.path.isfile(cache_file):
            with open(cache_file, 'w') as fd:
                fd.write(content)

        now = datetime.now()
        # use iso format rather than string format to make it more parsable
        log_line = json.dumps({
            'date': str(now), 
            'batch_id': batch_id,
            'groups': groups,
            'url': base64.urlsafe_b64decode(b64url),
        })
        cachelog.get_logger(batch_id, now.strftime('%Y%m%d')).info(log_line)
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True}


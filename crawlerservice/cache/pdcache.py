#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>

# 1. directory hierarchy: /data/Hproject/yy/batch_id/
# 2. log name: ip+date.log
#    purpose: tornado setup on different machine, rsync log merge.
# 3. log content: date, batch_id, group, URL, remote_ip.

from __future__ import print_function, division
from datetime import datetime

import base64
import hashlib
import json
import os
from datetime import date
from crawlerlog import path, cachelog

HPCACHEDIR = '/data/Hproject/'
today = date.today()
yy = str(today.year)
mm = '0' + str(today.month) if today.month < 10 else str(today.month)
dd = '0' + str(today.day) if today.day < 10 else str(today.day)


def pd_get_cache(url_hash, batch_id):
    try:
        assert len(batch_id) > 0

        absdir = os.path.join(HPCACHEDIR, yy, batch_id + '-' + yy + mm + dd)
        cache_file = os.path.join(absdir, url_hash)
        if os.path.isfile(cache_file):
            with open(cache_file) as fd:
                html = fd.read()
        else:
            return {'success': False}
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True, 'content': html}


def pd_set_cache(url_hash, batch_id, groups, content, refresh=False):
    try:
        assert len(batch_id) > 0

        absdir = os.path.join(HPCACHEDIR, yy, batch_id + '-' + yy + mm + dd)

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
            # 'url': base64.urlsafe_b64decode(b64url),
        })
        cachelog.get_logger(batch_id, now.strftime('%Y%m%d'), HPCACHEDIR).info(log_line)
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True}


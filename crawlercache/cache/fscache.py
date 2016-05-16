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
import logging
import os

from settings import FSCACHEDIR
from tools import log, ip


def get_logger(batch_id, today_str):
    """
        today_str: datetime.now().strftime('%Y%m%d')
    """

    def filename_in_logger_out():
        absdir = os.path.join(FSCACHEDIR, batch_id, 'meta')
        makedir(absdir)
        absfname = os.path.join(absdir, 
                                '{}_{}.log'.format(
                                    get_logger._ipaddr,
                                    get_logger._today_str)
                               )
        if not os.path.isfile(absfname):
            with open(absfname, 'a'):
                pass
        return log.init(batch_id, absfname, level=logging.INFO, size=100*1024*1024)

    if not hasattr(get_logger, '_ipaddr'):
        setattr(get_logger, '_ipaddr', ip.get_ip_address())

    if not hasattr(get_logger, '_today_str'):
        setattr(get_logger, '_today_str', today_str)
        setattr(get_logger, '_logger', filename_in_logger_out())

    if get_logger._today_str != today_str:
        setattr(get_logger, '_today_str', today_str)
        setattr(get_logger, '_logger', filename_in_logger_out())

    return get_logger._logger

def makedir(absdir):
    if not os.path.exists(absdir):
        os.makedirs(absdir)


def fs_get_cache(b64url, batch_id):
    try:
        assert batch_id != ''
        level1 = hashlib.sha1(b64url).hexdigest()[-1:]
        level2 = hashlib.md5(b64url).hexdigest()[-2:]
        absdir = os.path.join(FSCACHEDIR, batch_id, 'raw', 'latest', level1, level2)
        cache_file = os.path.join(absdir, b64url)
        if os.path.isfile(cache_file):
            with open(cache_file) as fd:
                html = fd.read()
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True, 'content': html}


def fs_set_cache(b64url, batch_id, groups, content, refresh=False):
    try:
        assert batch_id != ''
        level1 = hashlib.sha1(b64url).hexdigest()[-1:]
        level2 = hashlib.md5(b64url).hexdigest()[-2:]
        absdir = os.path.join(FSCACHEDIR, batch_id, 'raw', 'latest', level1, level2)
        cache_file = os.path.join(absdir, b64url)

        makedir(absdir)
        if refresh or not os.path.isfile(cache_file):
            with open(cache_file, 'w') as fd:
                fd.write(content)

        now = datetime.now()
        log_line = json.dumps({
            'date': str(now), 
            'batch_id': batch_id,
            'groups': groups,
            'url': base64.urlsafe_b64decode(b64url),
        })
        get_logger(batch_id, now.strftime('%Y%m%d')).info(log_line)
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True}


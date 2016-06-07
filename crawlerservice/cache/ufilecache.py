#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from secret import public_key, private_key
from tools import cachelog
from ucloud.ufile import putufile, downloadufile
from ucloud.ufile import bucketmanager

from dbconnector import dbwrapper

from cStringIO import StringIO
from datetime import datetime

import base64
import json
import hashlib
import requests
import string

def ensure_bucket(batch_key):
    if not hasattr(ensure_bucket, '_auth'):
        bucketmanager_handler = bucketmanager.BucketManager(public_key, private_key)
        setattr(ensure_bucket, '_auth', bucketmanager_handler)

    ret, resp = bucketmanager_handler.describebucket(batch_key)
    if ret[u'RetCode'] != 0:
        ret, resp = bucketmanager_handler.createbucket(batch_key, 'private')


def ufile_get_cache(batch_id, url_hash):
    if not hasattr(ufile_get_cache, '_auth'):
        down_auth = downloadufile.DownloadUFile(public_key, private_key)
        setattr(ufile_get_cache, '_auth', down_auth)

    try:
        filename = '{}_{}'.format(batch_id, url_hash)
        batch_key = batch_id.rsplit('-', 1)[0]
        ret, resp = ufile_get_cache._auth.download_stream(batch_key, filename)
        if resp.status_code != 200:

            if resp.status_code == 400:
                if json.loads(resp.content)[u'ErrMsg'] == u'bucket not exist':
                    ensure_bucket(batch_key)
                    raise Exception('{} bucket not exist, create, upload again'.format(batch_key))

            return {'success': False, 'error': resp.content}
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True, 'content': ret}


def ufile_set_cache(b64url, url_hash, batch_id, groups, content, refresh=False):
    if not hasattr(ufile_set_cache, '_auth'):
        put_auth = putufile.PutUFile(public_key, private_key)
        setattr(ufile_set_cache, '_auth', put_auth)

    try:
        sio = StringIO(content)
        filename = '{}_{}'.format(batch_id, url_hash)
        batch_key = batch_id.rsplit('-', 1)[0]
        ret, resp = ufile_set_cache._auth.putstream(batch_key, filename, sio)
        if resp.status_code != 200:

            if resp.status_code == 400:
                if json.loads(resp.content)[u'ErrMsg'] == u'bucket not exist':
                    ensure_bucket(batch_key)
                    raise Exception('{} bucket not exist, create, upload again'.format(batch_key))

            raise Exception('{} upload ufile error: {}'.format(batch_id, b64url))

        _groups = str(map(string.strip, groups.split(',')))[1:-1].replace('\'', '"')
        sql1 = ("insert into accessed (batch_id, groups, status, b64url, url_hash) "
                "values ('{}', '{{{}}}', '{}', '{}', '{}');".format(batch_id, _groups, 0, b64url, url_hash))
        sql2 = ("insert into cached (b64url, url_hash) values ('{}', '{}')"
                ";".format(b64url, url_hash))
        dbwrapper.execute(sql1)
        dbwrapper.execute(sql2)

        now = datetime.now()
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


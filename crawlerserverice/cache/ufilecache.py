#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from secret import public_key, private_key
from ucloud.ufile import putufile, downloadufile
from dbconnector import dbwrapper
from cStringIO import StringIO

import json
import hashlib
import requests

bucket_domain = 'crawlercache.ufile.ucloud.cn'
private_bucket = 'crawlercache'


def ufile_get_cache(b64url):
    if not hasattr(ufile_get_cache, '_auth'):
        down_auth = downloadufile.DownloadUFile(public_key, private_key)
        setattr(ufile_get_cache, '_auth', down_auth)

    try:
        hashkey = hashlib.sha256(b64url).hexdigest()
        url = ufile_get_cache._auth.private_download_url(private_bucket, hashkey, internal=True)
        resp = requests.get(url)
        if resp.status_code != 200:
            raise Exception('download ufile error: {}'.format(b64url))

    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True, 'content': resp.content}


def ufile_set_cache(b64url, batch_id, groups, content, refresh=False):
    if not hasattr(ufile_set_cache, '_auth'):
        put_auth = putufile.PutUFile(public_key, private_key)
        setattr(ufile_set_cache, '_auth', put_auth)

    try:
        sio = StringIO(content)
        hashkey = hashlib.sha256(b64url).hexdigest()
        ret, resp = ufile_set_cache._auth.putstream(private_bucket, hashkey, sio)
        if resp.status_code != 200:
            raise Exception('{} upload ufile error: {}'.format(batch_id, b64url))

        sql1 = ("insert into accessed (batch_id, status, b64url, url_hash) "
                "values ('{}', '{}', '{}', '{}');".format(batch_id, 0, b64url, url_hash))
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

#ufile_set_cache('rewre', 'qichacha', 'test', u'abcd3e')
#ufile_get_cache('rewre')

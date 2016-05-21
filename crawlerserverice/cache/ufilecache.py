#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from secret import public_key, private_key
from ucloud.ufile import putufile, downloadufile
from dbconnector import dbwrapper
from io import BytesIO

import hashlib

bucket_domain = 'crawlercache.ufile.ucloud.cn'
private_bucket = 'crawlercache'


def upload(url, content):
    if not hasattr(upload, '_auth'):
        put_auth = putufile.PutUFile(public_key, private_key)
        setattr(upload, '_auth', put_auth)

    if isinstance(content, unicode):
        content = content.encode('utf-8')
    bio = BytesIO(content)

    hashkey = hashkey = hashlib.sha256(url).hexdigest()
    ret, resp = upload._auth.putfile(private_bucket, hashkey, bio)
    assert resp.status_code == 200


def download(url):
    if not hasattr(download, '_auth'):
        down_auth = downloadufile.DownloadUFile(public_key, private_key)
        setattr(download, '_auth', down_auth)

    hashkey = hashkey = hashlib.sha256(url).hexdigest()
    ret, resp = down_auth.download_file(private_bucket, hashkey, private_savefile)
    assert resp.status_code == 200


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import qiniu
import requests

from dbconnector import dbwrapper
from secret import access_key, secret_key

bucket_domain = 'o6kz8oe5r.bkt.clouddn.com'
bucket_name = 'crawlercache'

def upload(source_url, content):
    if not hasattr(upload, '_auth'):
        qauth = qiniu.Auth(access_key, secret_key)
        setattr(upload, '_auth', qauth)

    hashkey = hashlib.sha256(source_url).hexdigest()
    token = upload._auth.upload_token(bucket_name, hashkey, 3600)

    ret, info = qiniu.put_data(token, hashkey, content)

    if ret is not None:
        print(ret)
        print(info)
    else:
        print(ret)
        print(info) # error message in info


def download(qiniukey):
    if not hasattr(download, '_auth'):
        qauth = qiniu.Auth(access_key, secret_key)
        setattr(download, '_auth', qauth)

    base_url = 'http://{}/{}'.format(bucket_domain, qiniukey)
    private_url = download._auth.private_download_url(base_url, expires=3600)
    r = requests.get(private_url)

    print(r.status_code)
    return r.content # str


def access_with_cache(qiniukey):
    """
    qiniukey: unique sha256 of url + created_time
    """

    sql = "select url, created_time from cached where url_hash='{}' order by created_time desc limit 1;".format(hashkey)
    ret = dbwrapper.execute(sql).results

    url, created_time = ret[0]
    qiniukey = hashlib.sha256(url + created_time).hexdigest()
    return download(qiniukey)


if __name__ == '__main__':
#    upload()
    download('http://developer.qiniu.com/code/v7/sdk/python.html')


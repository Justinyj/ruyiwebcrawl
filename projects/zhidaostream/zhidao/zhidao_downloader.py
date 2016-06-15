#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import time
from downloader.downloader import Downloader

HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
    'Cache-Control': 'max-age=0',
    'Host': 'zhidao.baidu.com',
    'Proxy-Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': 1,
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
}

def zhidao_downloader(url, batch_id, gap, method='get', timeout=10, encode='gb18030', error_check=True, refresh=False):
    if not hasattr(zhidao_downloader, '_batches'):
        setattr(zhidao_downloader, '_batches', {})

    if zhidao_downloader._batches.get(batch_id) is None:
        downloader = Downloader(request=True, gap=gap, batch_id=batch_id, timeout=timeout)
        downloader.login()
        downloader.update_header(HEADERS)
        zhidao_downloader._batches[batch_id] = downloader

    return zhidao_downloader._batches[batch_id].requests_with_cache(
                                                     url,
                                                     method,
                                                     encode=encode,
                                                     redirect_check=True,
                                                     error_check=error_check,
                                                     refresh=refresh)


def zhidao_download(url, batch_id, gap, method='get', timeout=10, encode='gb18030', error_check=True):
    for _ in range(2):
        content = zhidao_downloader(url, batch_id, gap, method, timeout, encode, error_check)
        if content != u'':
            return content
        time.sleep(gap)
    else:
        return False

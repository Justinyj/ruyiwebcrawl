#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from .downloader import Downloader

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

def zhidao_downloader(url, batch_id, gap, method='get', timeout=10, error_check=True):
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
                                                     encode='gb18030',
                                                     redirect_check=True,
                                                     error_check=error_check,
                                                     refresh=False)


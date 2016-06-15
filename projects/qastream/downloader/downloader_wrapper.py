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

class DownloadWrapper(object):
    def __init__(self, cacheserver):
        self.cacheserver = cacheserver
        self._batches = {}

    def download_with_cache(self, url, batch_id, gap, method, timeout, encoding, redirect_check, error_check, refresh, headers):

        if batch_id not in self._batches:
            downloader = Downloader(True, batch_id, self.cacheserver, gap, timeout)
            if isinstance(headers, dict) and headers:
                downloader.update_header(headers)
            download_with_cache._batches[batch_id] = downloader

        return download_with_cache._batches[batch_id].requests_with_cache(
                                                         url,
                                                         method,
                                                         encode=encoding,
                                                         redirect_check=True,
                                                         error_check=error_check,
                                                         refresh=refresh)


    def downloader_wrapper(self,
                           url,
                           batch_id,
                           gap,
                           method='get',
                           timeout=10,
                           encoding='utf-8',
                           redirect_check=True,
                           error_check=False,
                           refresh=False,
                           headers=headers,
                           cache_retry=2):
        for _ in range(cache_retry):
            content = download_with_cache(url,
                                          batch_id,
                                          gap,
                                          method,
                                          timeout,
                                          encoding,
                                          redirect_check,
                                          error_check,
                                          refresh,
                                          headers)
            if content != u'':
                return content
            time.sleep(gap)
        else:
            return u''

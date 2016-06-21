#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import time
from .downloader import Downloader


class DownloadWrapper(object):
    def __init__(self, cacheserver=None, headers={}):
        self.cacheserver = cacheserver
        self._batches = {}
        self.headers = headers if isinstance(headers, dict) else {}


    def download_with_cache(self, url, batch_id, gap, method, timeout, encoding, redirect_check, error_check, refresh):
        if batch_id not in self._batches:
            downloader = Downloader(batch_id, self.cacheserver, True, gap, timeout)
            if self.headers:
                downloader.update_header(self.headers)
            self._batches[batch_id] = downloader

        return self._batches[batch_id].requests_with_cache(
                                                         url,
                                                         method,
                                                         encoding=encoding,
                                                         redirect_check=True,
                                                         error_check=error_check,
                                                         refresh=refresh)


    def downloader_wrapper(self,
                           url,
                           batch_id,
                           gap,
                           method='get',
                           timeout=10,
                           encoding=None,
                           redirect_check=True,
                           error_check=False,
                           refresh=False,
                           cache_retry=2):
        for _ in range(cache_retry):
            content = self.download_with_cache(url,
                                               batch_id,
                                               gap,
                                               method,
                                               timeout,
                                               encoding,
                                               redirect_check,
                                               error_check,
                                               refresh)
            if content != u'':
                return content
            time.sleep(gap)
        else:
            return u''

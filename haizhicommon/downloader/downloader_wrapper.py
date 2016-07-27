#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import time
from .downloader import Downloader


class DownloadWrapper(object):
    def __init__(self, cacheserver=None, headers={}, region_name='ap-northeast-1'):
        self.cacheserver = cacheserver
        self._batches = {}
        self.headers = headers if isinstance(headers, dict) else {}
        self.region_name = region_name


    def download_with_cache(self, url, batch_id, gap, method, timeout, encoding, redirect_check, error_check, data, refresh):
        if batch_id not in self._batches:
            downloader = Downloader(batch_id, self.cacheserver, True, gap, timeout, region_name=self.region_name)
            if self.headers:
                downloader.update_header(self.headers)
            self._batches[batch_id] = downloader

        return self._batches[batch_id].requests_with_cache(
                                                         url,
                                                         method,
                                                         encoding=encoding,
                                                         redirect_check=True,
                                                         error_check=error_check,
                                                         data=data,
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
                           data=None,
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
                                               data,
                                               refresh)
            if content != u'':
                return content
            time.sleep(gap)
        else:
            return u''

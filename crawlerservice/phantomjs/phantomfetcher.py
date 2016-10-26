#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import json
import time
import copy

from tornado.curl_httpclient import CurlAsyncHTTPClient
import tornado.httpclient
import tornado.ioloop

class PhantomFetcher(object):

    default_options = {
        'headers': {},
        'allow_redirects': True,
        'use_gzip': True,
        'rimeout': 1,
    }

    def __init__(self,
                 phantomjs_server,
                 pool_size=10,
                 async=False):
        self.phantomjs_server = phantomjs_server
        self.async = async
        if self.async is True:
            self.http_client = CurlAsyncHTTPClient(max_clients=pool_size, io_loop=tornado.ioloop.IOLoop())
        else:
            self.http_client = tornado.httpclient.HTTPClient(max_clients=pool_size)

    def parse_option(self, url, method='GET', **kwargs):
        fetcher = copy.deepcopy(self.default_options)
        fetcher['url'] = url
        fetcher['method'] = method
        fetcher['headers']['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'

        headers = kwargs.pop('headers', {})
        fetcher['headers'].update(headers)

        js_script = kwargs.pop('js_script', '')
        if js_script:
            fetcher['js_script'] = js_script
            fetcher['js_run_at'] = kwargs.pop('js_run_at', 'document-end')

        fetcher['load_images'] = kwargs.pop('load_images', False)
        fetcher.update(kwargs)
        print('fetcher: ', fetcher)
        return fetcher

    def fetch(self, url, **kwargs):
        start_time = time.time()
        fetcher = self.parse_option(url, **kwargs)
        request_conf = { 'follow_redirects': False }
        if 'timeout' in fetcher:
            request_conf['connect_timeout'] = fetcher['timeout']
            request_conf['request_timeout'] = fetcher['timeout'] + 1

        def handle_error(error):
            result = {
                'status_code': getattr(error, 'code', 599),
                'error': error,
                'content': '',
                'time': time.time() - start_time,
                'orig_url': url,
                'url': url,
            }
            return result

        def handle_response(response):
            if not response.body:
                return handle_error(Exception('no response body from phantomjs'))

            try:
                result = json.loads(response.body)
                if response.error:
                    result['error'] = response.error
            except Exception as e:
                return handle_error(e)
            return result


        try:
            http_request = tornado.httpclient.HTTPRequest(
                    method='POST',
                    url=self.phantomjs_server,
                    body=json.dumps(fetcher),
                    **request_conf
            )
            if self.async is True:
                self.http_client.fetch(http_request, handle_response)
            else:
                return handle_response( self.http_client.fetch(http_request) )
        except tornado.httpclient.HTTPError as e:
            if e.response:
                return handle_response(e.response)
            else:
                return handle_error(e)
        except Exception as e:
            return handle_error(e)

if __name__ == '__main__':
    # baidu calculator: http://www.baidu.com/aladdin/js/calculator/calculator1.html?v=20141113
    import urllib
    url = 'https://www.baidu.com/s?&wd={}'
    url = url.format( urllib.quote('三加二十') )

    url = 'https://m.baidu.com/s?word={}'
    url = url.format( urllib.quote('三加二十') )

    fetcher = PhantomFetcher('http://localhost:8001', async=False)
    res = fetcher.fetch(url)

    print(res.keys())
    print(res[u'status_code'], res[u'headers'], res[u'cookies'])


    open('a.html', 'w').write(res[u'content'].encode('utf-8'))

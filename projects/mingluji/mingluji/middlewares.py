# -*- coding: utf-8 -*-
from downloader.downloader_wrapper import DownloadWrapper
import scrapy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
BATCH_ID = 'mingluji-201606'
SERVER = 'http://192.168.1.179:8000/'


class MyMiddleWare(object):

    def process_request(self, request,  spider):
        url = request.url
        m = DownloadWrapper(SERVER)
        content = m.downloader_wrapper(url, BATCH_ID, 2)
        if content:
            response = scrapy.http.response.html.HtmlResponse(url, encoding='utf-8', body=content)
            return response
        return

'''
    def process_response(self, request, response, spider):
        url=response.url
        if response.status not in [200, 301]:
            f.write(response.url)
            return response
        m=Cache(BATCH_ID)
        content=m.get(url)
        if not content:
        	new_content=response.body
        	m.post(url,new_content)
              #print 'I am pppppppppppppppposting to Cache'
        return response
'''

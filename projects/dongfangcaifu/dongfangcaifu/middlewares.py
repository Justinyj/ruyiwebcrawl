# -*- coding: utf-8 -*-
import scrapy
import sys

from downloader.downloader_wrapper import DownloadWrapper
reload(sys)
sys.setdefaultencoding('utf-8')
BATCH_ID = 'dongfang-201606'
url='http://data.eastmoney.com/Notice'
SERVER='http://192.168.1.179:8000/'

class MyMiddleWare(object):
    def process_request(self, request,  spider):
        url = request.url
        m = DownloadWrapper(SERVER)
        content = m.downloader_wrapper(url,BATCH_ID,3)
        if content:
            response = scrapy.http.response.html.HtmlResponse(
                    url, encoding='utf-8', body=content)
            return response
        return
m = DownloadWrapper(SERVER)

'''
m=Cache(BATCH_ID)
print m.post('test','content3')
print m.get('http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page=29718')
'''
# -*- coding: utf-8 -*-
import scrapy
import sys

from downloader.downloader_wrapper import DownloadWrapper
reload(sys)
sys.setdefaultencoding('utf-8')
BATCH_ID = 'dongfang-201606test'
url='http://data.eastmoney.com/Notice'
SERVER='http://192.168.1.179:8000/'
m = DownloadWrapper(SERVER)
#content = m.downloader_wrapper('http://data.eastmoney.com/Notice/Noticelist.aspx',BATCH_ID,0,encoding='gb2312',refresh=True)
#print content
class MyMiddleWare(object):
    def process_request(self, request,  spider):
        url = request.url
        m = DownloadWrapper(SERVER)
        content = m.downloader_wrapper(url,BATCH_ID,3,encoding='gb2312')
        if content:
            response = scrapy.http.response.html.HtmlResponse(
                    url, encoding='utf-8', body=content)
            return response
        return

'''
m=Cache(BATCH_ID)
print m.post('test','content3')
print m.get('http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page=29718')
'''
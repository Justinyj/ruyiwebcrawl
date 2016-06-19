# -*- coding: utf-8 -*-
from downloader.cache import Cache
import sys
import re
import requests
reload(sys)
sys.setdefaultencoding('utf-8')
BATCH_ID = 'dongfang-201606test'
m = Cache(BATCH_ID,'http://192.168.1.179:8000/')
url = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page=33333'
content = m.get(url)
#print requests.get(url).text
print '更多公告'  in content
OK = 0
NO = 0
for index in range(1, 2000):
    url = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page={}'.format(
        index)
    content = m.get(url)
    if content:
        if '更多公告' in content:
            OK += 1
        else:
            NO += 1
print NO, OK
#检测指定区间内正常网页和显示不完全网页的对比
#所谓的显示不完全表现为网页爬取正常，但是列表框内没有那50个公告列表以及连接

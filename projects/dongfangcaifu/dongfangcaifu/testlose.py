# -*- coding: utf-8 -*-
from cache import Cache
import sys
import re
import requests
reload(sys)
sys.setdefaultencoding('utf-8')
BATCH_ID = 'dongfang-201606'
m = Cache(BATCH_ID)
url = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page=33333'
content = m.get(url)
#print requests.get(url).text
print '更多公告'  in content
OK = 0
NO = 0
for index in range(20000, 35172):
    url = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page={}'.format(
        index)
    content = m.get(url)
    if content:
        if '更多公告' in content:
            OK += 1
        else:
            NO += 1
print NO, OK
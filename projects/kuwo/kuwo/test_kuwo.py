from __future__ import print_function, division

import requests
import time
import lxml.html
from collections import Counter
# import scrapy

# HEADERS = {
#     'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
#     'Accept-Encoding': 'gzip, deflate, sdch',
#     'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
#     'Cache-Control': 'max-age=0',
#     'Connection': 'keep-alive',
#     'Upgrade-Insecure-Requests': 1,
#     'Host': 'data.eastmoney.com',
# }


url = "http://bd.kuwo.cn/mpage/api/artistSongs?artistid=119027&pn=0&rn=20&bdfrom=haizhi&c=1m496rxeda48"
gcounter = Counter()

def func():
    global url, gcounter

    for i in range(500):
        print(gcounter['error'], gcounter['count'])
        # time.sleep(0.5)
        gcounter['count'] += 1

        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200 or r.url != url:
                gcounter['error'] += 1
                print(r.status_code, r.url, r.headers)
            else:
                print(r.content)
        except Exception as e:
            gcounter['error'] += 1
            print(e)

    print('result: ', gcounter['error'], gcounter['count'])

func()
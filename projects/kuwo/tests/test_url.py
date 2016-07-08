#encoding:utf-8

#遍历一遍 api：歌手列表 的页数参数， 计算缺失率，（即500 internal server error）

from __future__ import print_function, division

import requests
import time
import lxml.html
from collections import Counter


base_url = "http://bd.kuwo.cn/mpage/api/artistList?pn={}&rn=1&bdfrom=haizhi&c=1m496rxeda48"  #歌手列表api的url
gcounter = Counter()

def func():
    global url, gcounter

    for i in range(66677):   #66677 是当前的歌手个数，偷懒没有用api返回
        print(gcounter['error'], gcounter['count'])
        # time.sleep(0.5)
        gcounter['count'] += 1
        url = base_url.format(i)

        try:
            r = requests.get(url, timeout=10)
            if r.status_code != 200 or r.url != url:
                gcounter['error'] += 1
                print(r.status_code, r.url, r.headers)
            # else:
            #     print(r.content)
        except Exception as e:
            gcounter['error'] += 1
            print(e)

    print('result: ', gcounter['error'], gcounter['count'])

func()
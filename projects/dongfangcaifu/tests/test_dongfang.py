# -*- coding: utf-8 -*-
import json
import time
import requests
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

session = requests.Session()
session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30,
              pool_maxsize=30, max_retries=3))


def test_page():
    # 50 notices per page
    global session
    page_url = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page=5'
    error_count = 0

    for i  in range(500):
        resp = session.get(page_url, timeout=10)
        print(resp.headers['Content-Type'])
        if '更多公告' not in resp.text:
            print resp.content
            print(resp.status_code, resp.url)
            print(i,)
            error_count += 1
            if resp.url == page_url:
                print('url same, still error')
        time.sleep(2)
    print('Error percentage: {}'.format(error_count / i))

def test_notice():
    global session
    notice_url='http://data.eastmoney.com/notice/20160618/2Wvl2aXu2pMEbA.html'
    error_count = 0

    for i  in range(500):
        resp = session.get(notice_url, timeout=10)
        print(resp.headers['Content-Type'])
        if '原文' not in resp.text:
            print resp.content
            print(resp.status_code, resp.url)
            print(i,)
            error_count += 1
            if resp.url == notice_url:
                print('url same, still error')
        time.sleep(2)
    print('Error percentage: {}'.format(error_count / i))
#test_notice()
test_page()
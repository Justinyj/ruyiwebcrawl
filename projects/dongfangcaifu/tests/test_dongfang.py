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
#test_page()

'''
测试结果：
1.问题表征：scrapy设置download delay为2秒时，进行类似test_page的爬取，有10%的网页会显示不完全。
所谓的不完全是指‘tableCont’这个表格里的五十个无法显示，其它地方正常。
2.浏览器连按10多次，直接被BAN，显示403
3.不设置delay用土制法进行类似test_notice的爬取，也很容易被BAN
4.用此文件里的程序，设置成sleep3秒时，跑若干次，每次循环五百次，没出现被BAN
5.用此文件里的程序，设置成sleep2秒时，跑若干次，会被BAN
虽然‘被BAN’和‘显示不完全是不同的错误情况’，但有理由认为3秒比2秒是个更合适的值，进行尝试。
6.用srcapy，download delay设置成3秒，（期间将middleware里的cache更换成downloader），更换新的batch-ID进行爬取，用testlose.py测试结果，
目前得到1-1000区间内：不完整0，完整346个网页 （此前10%的缺失率也是这个文件测出）

最后结论：
调整间隔为3秒进行爬取，继续观察
'''

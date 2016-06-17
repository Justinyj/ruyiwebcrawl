# -*- coding: utf-8 -*-
from downloader.downloader import Downloader
import lxml.html
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


def generate_json(url, content):
    dom = lxml.html.fromstring(content)
    raw_title = dom.xpath('//div[@class="content"]/h4/text()')
    raw_content = dom.xpath('//div[@class="content"]//pre/text()')

    title = ''.join(raw_title).strip()
    content = ''.join(raw_content).strip()
    item = {
        'title': title,
        'url': url,
        'content': content,
    }
    return json.dumps(item, ensure_ascii=False)


def download_url(url):
    cacheserver = 'http://192.168.1.179:8000/'
    batch_id = 'dongfangcaifu-201606'
    url = url
    #url = 'http://data.eastmoney.com/notice/20160617/2Wvl2aWuYwihKD.html'
    m = Downloader(batch_id, cacheserver, request=True)
    content = m.request_download(url, encoding='gb2312')
    return content


def run(filename):
    with open(filename, 'r') as source:
        url = source.readline().strip()
        if not url:
            return
        content = download_url(url)
        ret = generate_json(url, content)
        f = open('dongfang_outpu.json', 'a')
        f.write(ret)
        f.close()

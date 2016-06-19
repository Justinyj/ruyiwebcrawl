# -*- coding: utf-8 -*-
from downloader.downloader import Downloader
from downloader.downloader_wrapper import DownloadWrapper
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
    m = DownloadWrapper(cacheserver)
    content = m.downloader_wrapper(url, batch_id, 0.5, encoding='gb2312')
    return content

def run(filename):
    with open(filename, 'r') as source:
        while 1:
            url = source.readline().strip()
            if not url:
                return
            content = download_url(url)
            if not content:
                print 'error:{}'.format(url)
                continue
            ret = generate_json(url, content)
            f = open('notice_output.json', 'a')
            f.write(ret + '\n')
            f.close()

#run('url_per_notice.txt')
#download_url('http://data.eastmoney.com/notice/20160616/2Wvl2aVspAUtZt.html')

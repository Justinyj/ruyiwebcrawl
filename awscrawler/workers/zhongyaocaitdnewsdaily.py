#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

from datetime import datetime

import json
import urllib
import re
import pytz
import urlparse
import lxml.html
import time
import requests
import datetime
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('..')
from downloader.cacheperiod import CachePeriod
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper
from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER



def get_news_content(url):
    content = requests.get(url).text
    dom = lxml.html.fromstring(content)
    news_content = dom.xpath('//div[@id="infoContent"]//text()')
    return '\n'.join(news_content).strip()

def parse_list_page(content):
    # 重要逻辑：先获得分类栏的种类所对应的ID，之后通过解析每条新闻的url确定其种类
    # 这是一个保险化的规范流程，非必要，对网页足够信赖也可以冒着一定风险,直接在代码中定下ID-对应栏目种类
    # 菜单共有六个栏目分类： 产地快讯 ,市场快讯 ,品种分析 ,市场点评 ,产业观察 ,产业报告
    dom = lxml.html.fromstring(content)
    menu_dic = {}
    menu_node_list = dom.xpath('//li[@menuid="http://www.zyctd.com/zixun/"]//div//a')  # //div[@class="snavList"]')
    for menu_node in menu_node_list:
        menuid_url = menu_node.xpath('./@menuid')[0]
        menuid     = re.findall('(\d+)', menuid_url)[0]
        menu_type  = menu_node.xpath('./text()')[0]
        menu_dic[menuid]   = menu_type                 # 示例： menu_dic['201'] = '产地快讯'

    result_list = []
    news_node_list = dom.xpath('//div[@id="hasInfoRegion"]//li')
    for news_node in news_node_list:
        news_title      = news_node.xpath('./h2/a/text()')[0]                   # 如果觉得[0]不安全，可以考虑额外增加列表为空的判断，但是会使代码更难读
        news_url        = news_node.xpath('./h2/a/@href')[0]                    # 用 ''.join()可以避免if判断，也会让人感觉奇怪
        news_desc       = news_node.xpath('.//p[@class="info"]//text()')[0].strip()

        news_info_node  = news_node.xpath('.//p[@class="ft"]')[0]
        news_date       = news_info_node.xpath('.//span[@class="g9"]//text()')[0]
        news_keyword_list    = news_info_node.xpath('.//span[@class="r"]//text()')
        news_keyword_list       = news_keyword_list[1:-1]                               # 第一个元素为‘药材’字符，最后一个元素为制表符等， 此种语法可以应对不存在药材关键字字段的新闻
        result = {
            'news_title'        : news_title,
            'news_url'          : news_url,
            'news_desc'         : news_desc,
            'news_date'         : news_date,
            'news_keyword_list' : [keyword.strip() for keyword in news_keyword_list],   #  每个药材字符都需要strip
            'access_time'       : datetime.datetime.utcnow().isoformat(),
        }
        news_menuid = re.findall('www.zyctd.com/zixun/(\d+)/', news_url)[0]
        result['news_type'] = menu_dic[news_menuid]
        if u'快讯' in result['news_type']:
            result['news_content'] = result['news_desc']                              # 快讯属于短新闻，正文和简述是一样的
        elif u'产业报告' == result['news_type']:                               # 产业报告不爬取，  (此处会有极轻微的重复计算嫌疑)
            continue
        else:
            result['news_content'] = get_news_content(news_url)                         # 属于需要爬的长新闻
        result_list.append(result)
    return result_list

def check_date_ok(url):                                  # 药通网的新闻每天北京时间10~12点更新，爬虫可以设成北京时间13~14点爬取，
    print 'check date'
    now = datetime.datetime.utcnow()
    content = requests.get(url).text
    dom = lxml.html.fromstring(content)
    date_list = dom.xpath('//span[@class="g9"]//text()')

    date = date_list[0]
    news_date = time.strptime(date,'%Y-%m-%d %H:%M')
    yesterday_date = datetime.date.today() - datetime.timedelta(days=1)
    yesterday_zero = yesterday_date.timetuple()   #当天上海时间0点
    print news_date
    print yesterday_zero
    return news_date > yesterday_zero


def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper(None, headers))
    if not hasattr(process, '_cache'):
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))
    if not hasattr(process, '_regs'):
        setattr(process, '_regs', {
            'home_page' : re.compile('http://www.zyctd.com/zixun/'),
            'list_page' : re.compile('http://www.zyctd.com/zixun-(\d+).html')
        })
    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)
    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        print label
        if label == 'home_page':
            url_pattern = 'http://www.zyctd.com/zixun-{}.html'
            content = process._downloader.downloader_wrapper(
                url,
                batch_id,
                gap,
                timeout = timeout,
                encoding = 'utf-8',
                refresh = True)
            page_content = re.findall('var pageCount = parseInt\(\'(\d+)\'\)', content)  # 在网页元素中没有，通过js代码段获得
            if not page_content:
                return False
            page_num = int(page_content[0])
            print (page_num)
            urls = []

            for page in range(2,page_num):
                print page
                page_url = url_pattern.format(page)
                if not check_date_ok(page_url):         # 由于中药材天地网每天更新新闻只有十多页，逐页检查虽然会浪费访问次数，但是并不严重
                    break
                urls.append(page_url)
            print len(urls)
            manager.put_urls_enqueue(batch_id, urls)

            result_list = parse_list_page(content)               # 首页本身作为第一页也有新闻信息，也要进行分析
            return process._cache.post(url, json.dumps(result_list, ensure_ascii=False), refresh=True)

        elif label == 'list_page':
            content = process._downloader.downloader_wrapper(
                url,
                batch_id,
                gap,
                timeout = timeout,
                encoding = 'utf-8',
                refresh = True)
            result_list = parse_list_page(content)
            return process._cache.post(url, json.dumps(result_list, ensure_ascii=False), refresh=True)

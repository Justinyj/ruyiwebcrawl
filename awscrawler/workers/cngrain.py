#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>
# 网站结构分三层：列表翻页，单个市场页，单个产品的价格历史。
from __future__ import print_function, division

import json
import urllib
import re
import urlparse
import lxml.html
from datetime import datetime
import sys
import time
reload(sys)
sys.setdefaultencoding('utf-8')
from downloader.caches3 import CacheS3
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME


def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    today_str = datetime.now().strftime('%Y%m%d')
    get_logger(batch_id, today_str, '/opt/service/log/').info('process {}'.format(url))

    if not hasattr(process, '_cache'):
        head, tail = batch_id.split('-')
        setattr(process, '_cache', CacheS3(head + '-json-' + tail))

    if not hasattr(process, '_downloader'):
        headers = {
                    'Cookie':'AJSTAT_ok_times=1; ant_stream_5762b612883d9=1470748235/1519574204; ASP.NET_SessionId=rpdjsrnmq3ybp0f4cnbdewm1; __utmt=1; bow_stream_5762b612883d9=13; __utma=240343830.1666180114.1470705813.1470719553.1470752966.3; __utmb=240343830.6.10.1470752966; __utmc=240343830; __utmz=240343830.1470705813.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
                    'Host':'datacenter.cngrain.com',
            }
        setattr(process, '_downloader', DownloadWrapper(None, headers, REGION_NAME))

    if not hasattr(process, '_regs'):
        setattr(process, '_regs', {
                'home' : re.compile('http://datacenter.cngrain.com/NewPrice.aspx'),
                'market': re.compile('http://datacenter.cngrain.com/PriceMainMark.aspx\?MarketId=(.*)')
            })
    if not hasattr(process, '_pattern'):
        setattr(process, '_pattern', {
            'market'    : 'http://datacenter.cngrain.com/PriceMainMark.aspx',
            'history'   : 'http://datacenter.cngrain.com/amline/PriceMarkXml.aspx{}'
        })


    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)
    gap = max(gap - other_batch_process_time, 0)

    for label, reg in process._regs.iteritems():
        m = reg.match(url)
        if not m:
            continue
        if label == 'home':
            data = {
                #'__EVENTTARGET':, #最后两位表示页数，其值不能超过11
                '__EVENTARGUMENT':'',
                '__ZIPSTATE': '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',
                '__VIEWSTATE':'',
                #'__EVENTVALIDATION':,
                'ctl00$txtTitle':'',
            }
            
            content = process._downloader.downloader_wrapper(url, 
                batch_id,
                gap,
                method = 'get',
                timeout = timeout,
                refresh = True,
                encoding = 'utf-8')  #第一页使用get,得到ZIPSTATE参数,之后在循环内持续利用__EVENTTARGET参数翻页同时更新ZIPSTATE参数
            if content == '':
                return False
            while 1:
                dom = lxml.html.fromstring(content) #开始解析当前页
                market_suffixes = dom.xpath('//a[contains(@href,"MarketId")]/@href')
                if not market_suffixes:
                    get_logger(batch_id, today_str, '/opt/service/log/').info('No market_suffixes')
                    get_logger(batch_id, today_str, '/opt/service/log/').info(content)
                    return False

                market_suffixes_set = set(market_suffixes)          #去重，但是对于市场名重复延续到下一页的情况无效，会重复多爬一次
                market_url_list = [urlparse.urljoin(process._pattern['market'], suffix) for suffix in market_suffixes_set]
                manager.put_urls_enqueue(batch_id, market_url_list) #完成本页的处理，将市场名入队，接下去的操作全是为了翻页

                page_label = dom.xpath('//td[@colspan="10"]//span')[0]  #在所有页数里，只有当前页的标签是span，定位到当前页
                next_sibling_list = (page_label.xpath('./following-sibling::a')) #定位下一页，下一页不存在时则结束，（即使是网页上的...按钮，在此种判断里也会算存在下一页）
                if not next_sibling_list:
                    return

                next_sibling = next_sibling_list[0]
                next_raw_js = next_sibling.xpath('./@href')[0]  # 其形式为 :   "javascript:__doPostBack('ctl00$ContentPlaceHolder1$DG_FullLatestPrice$ctl24$ctl01','')" 
                eventtarget = re.findall('\(\'(.*)\',',next_raw_js)[0]
                data['__EVENTTARGET'] = eventtarget

                last = data['__ZIPSTATE'] #用来储存上一次的ZIPSTATE参数，如果新参数失败就换旧的使用——实践过程中发现某页的ZIPSTATE有小概率对下一页失效
                data['__ZIPSTATE'] = (dom.xpath('//input[@name="__ZIPSTATE"]/@value'))[0]  
                data['__EVENTVALIDATION'] = (dom.xpath('//input[@name="__EVENTVALIDATION"]/@value'))[0]  #更新参数

                for _ in range(0,3): #开始对下一页发请求，绝大多数失败都发生在这一步，慎重
                    try:
                        content = process._downloader.downloader_wrapper(url,
                                            batch_id,
                                            gap,
                                            method = 'post',
                                            timeout = timeout,
                                            refresh = True,
                                            data = data,
                                            encoding = 'utf-8')

                        if content == '' or 'sent a request that this server could not understand' in content or 'bad request' in content:
                           get_logger(batch_id, today_str, '/opt/service/log/').info('change ZIPSTATE')
                           get_logger(batch_id, today_str, '/opt/service/log/').info('change ZIPSTATE')
                           data['__ZIPSTATE'] = last #使用上一次的参数，不考虑连续两次失败，实际调试中也没遇到过
                           continue
                    except Exception, e:
                        get_logger(batch_id, today_str, '/opt/service/log/').info(e)
                        continue
                    break
                else:
                    get_logger(batch_id, today_str, '/opt/service/log/').info('failed 3 times')
                    return False

        elif label == 'market':  #开始处理市场页，同时在此处理价格历史，加入到产品信息生成结果
            get_logger(batch_id, today_str, '/opt/service/log/').info('in market page')
            market_id = url[url.find('=') + 1:]
            url = url.replace(market_id, urllib.quote(market_id))
            content = process._downloader.downloader_wrapper(url,
                        batch_id,
                        gap,
                        timeout = timeout,
                        refresh = True,
                        encoding = 'utf-8',
                        redirect_check = False
            )

            dom = lxml.html.fromstring(content)
            title = dom.xpath('//title/text()')
            if title:
                title = title[0]
            result = {}
            result['market'] = title.strip()
            result['product_list'] = []

            table_node = dom.xpath('//table[@class="data_table"]')[0] #得到产品表格
            products_nodes = table_node.xpath('.//tr')[1:-1]          #去掉表头和尾巴

            newest_time = None
            for product_node in products_nodes:   #市场页会有相同产品在不同时间的批次，以此为根据去重
                report_time = product_node.xpath('./td[9]/text()')
                if not newest_time:  
                    newest_time = report_time
                if newest_time != report_time:
                    break

                history_url  = process._pattern['history'].format(product_node.xpath('./td[10]/a/@href')[0])
                get_logger(batch_id, today_str, '/opt/service/log/').info('The history_url is :{}'.format(history_url))
                content = process._downloader.downloader_wrapper(history_url,
                        batch_id,
                        gap,
                        timeout = timeout,
                        refresh = True,
                        encoding = 'utf-8')

                if content:  #有的价格历史会显示‘数据还在完善中‘
                    dom_history = lxml.html.fromstring(content)
                    date_list = dom_history.xpath('//series//value/text()')
                    price_list = dom_history.xpath('//graph//value/text()')
                    history_dic = dict(zip(date_list, price_list)) 
                else:
                    history_dic = {} 

                product_item = {
                    'variety' : product_node.xpath('./td[1]/text()')[0].strip(),
                    'level'   : product_node.xpath('./td[2]/text()')[0].strip(),
                    'price_type':product_node.xpath('./td[5]/text()')[0].strip(),
                    'produce_year': product_node.xpath('./td[6]/text()')[0].strip(),
                    'produce_area': product_node.xpath('./td[7]/text()')[0].strip(),
                    'deliver_area': product_node.xpath('./td[8]/text()')[0].strip(),
                    'price_history': history_dic,
                }
                result['product_list'].append(product_item)
                result['url'] = url
            return process._cache.post(url, json.dumps(result, ensure_ascii = False))
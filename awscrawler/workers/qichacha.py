#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 注意： 企查查不能与其他爬虫同时爬取，必须单独运行
# 爬取逻辑：  1： 搜索公司名，将搜索结果前十页的公司详情页及投资页加入待爬取队列，将别名映射存入period cache
#           2： 解析投资页面和详情页面，若json内容不为空则存入period cache,否则丢弃

from __future__ import print_function, division
import sys
import json
import urllib
import re
import urlparse
import lxml.html
import requests
from datetime import datetime
from downloader.cacheperiod import CachePeriod
from downloader.cache import Cache
from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from parsers.qiparser2 import QiParser
from crawlerlog.cachelog import get_logger
from settings import REGION_NAME, CACHE_SERVER

reload(sys)
sys.setdefaultencoding('utf-8')
SITE = 'http://www.qichacha.com'

def process(url, batch_id, parameter, manager, other_batch_process_time, *args, **kwargs):
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        cookie = kwargs.get('cookie', None)
        # cookie = "gr_user_id=0fceb70d-e0ab-4c16-8f21-d49b5d242b0e; PHPSESSID=ltro2cjbvonlg6mu4hupe7dcv1; CNZZDATA1254842228=371101890-1469690209-null%7C1472547698"

        if cookie:
            headers.update({'Cookie': cookie})
        setattr(process, '_downloader', DownloadWrapper(None, headers))
    if not hasattr(process, '_cache'):
        setattr(process, '_cache', CachePeriod(batch_id, CACHE_SERVER))

    if not hasattr(process, '_regs'):
        setattr(process, '_regs', {
            'search': re.compile(urlparse.urljoin(SITE, 'search\?key=(.+?)&index=(\d+)&p=(\d+)')),
            'detail': re.compile(urlparse.urljoin(SITE, 'company_getinfos\?unique=(.+?)&companyname=(.+?)&tab=base')),
            'invest': re.compile(urlparse.urljoin(SITE, 'company_getinfos\?unique=(.+?)&companyname=(.+?)(?:&p=(\d+))?&tab=touzi(?:&box=touzi)?')),
        })

    method, gap, js, timeout, data = parameter.split(':')
    gap = float(max(0, float(gap) - other_batch_process_time))
    timeout= int(timeout)
    today_str = datetime.now().strftime('%Y%m%d')

    # if kwargs and kwargs.get("debug"):
    #     get_logger(batch_id, today_str, '/opt/service/log/').info('start download')
    def reformat(info):     # 将info按企查查页面顺序插入队列
        temp = info['info']
        del info['info']
        info['info'] = []
        info['info'].append(("统一社会信用码", temp['unified_social_credit_code']))
        info['info'].append(("注册号", temp['registration_id']))
        info['info'].append(("组织机构代码", temp['organization_code']))
        info['info'].append(("经营状态", temp['status']))
        info['info'].append(("公司类型", temp['business_type']))
        info['info'].append(("成立日期", temp['begin']))
        info['info'].append(("法定代表", temp['legal_person']))
        info['info'].append(("注册资本", temp['registered_capital']))
        info['info'].append(("营业期限", temp['end']))
        info['info'].append(("登记机关", temp['registration_authority']))
        info['info'].append(("发照日期", temp['approval_date']))
        info['info'].append(("企业地址", temp['address']))
        info['info'].append(("经营范围", temp['business_scope']))
        return info


    def parse_company_investment(tree):     # 解析对外投资页面，将子公司存入sub_companies字段下
        invest_dict = {'sub_companies': [] }
        for sub_company in tree.cssselect('.list-group a.list-group-item'):
            sub_name = sub_company.cssselect('span.clear .text-lg')[0].text_content().strip()
            href = sub_company.get('href')
            province, key_num = href.rsplit('_', 2)[-2:]
            invest_dict['sub_companies'].append({
                'name': sub_name,
                'key_num': key_num,
                'province': province,
                'href': href,
            })
        return invest_dict

    def parser_patch(tree, all_info):
        shareholders = tree.xpath("//table[@class='table table-bordered']/tr")
        for sh in shareholders[1:]:
            name = sh.xpath('./td[1]/a[1]/text()')[0]
            subscribe_money = sh.xpath("./td[2]/text()")[0]
            actual_money = sh.xpath("./td[3]/text()")[0]
            all_info['shareholders'].append({ 'name':name, 'subscribe_money': subscribe_money, 'actual_money': actual_money})
        names = tree.xpath("//div[@class='clear']/a[@class='text-lg']/text()")
        positions = tree.xpath("//div[@class='clear']/small/text()")

        for name,pos in zip(names, positions):
            all_info['executives'].append({'name': name, 'position': pos})
        return all_info


    content = process._downloader.downloader_wrapper(url,
        batch_id,
        gap,
        method,
        timeout=timeout,
        encoding='utf-8')

    cookie = kwargs.get('cookie', None)
    if not cookie:
        get_logger(batch_id, today_str, '/opt/service/log/').info("No cookie in worker")
        return False

    if content == '':
        get_logger(batch_id, today_str, '/opt/service/log/').info("no content")
        content = requests.get(url, cookies={1: cookie}).text
        if content:
            get_logger(batch_id, today_str, '/opt/service/log/').info('got content')
        if not content and url.endswith("tab=touzi&box=touzi"):
            get_logger(batch_id, today_str, '/opt/service/log/').info("void invest page")
            return True




    invest_pat = "http://www.qichacha.com/company_getinfos?unique={key_num}&companyname={name}&p={p}&tab=touzi&box=touzi"
    main_pat = "http://www.qichacha.com/company_getinfos?unique={key_num}&companyname={name}&tab=base"
    search_pat = "http://www.qichacha.com/search?key={name}&index=0&p={p}"
    parser = QiParser()
    tree = lxml.html.fromstring(content.replace('<em>', '').replace('</em>', ''))

    # if kwargs and kwargs.get("debug"):
        # print('start parsing url')

    for label, reg in process._regs.iteritems():
        m = reg.match(url)

        if not m:
            continue

        if label == 'search':   # 搜索页面解析
            comp_name = urllib.unquote(m.group(1))
            page = int(m.group(3))
            dic = { 'search_name': comp_name, 'names': [] }
            urls = []
            pages = tree.xpath(".//a[@id=\"ajaxpage\"]/text()")
            if '>' in pages and page < 10:
                urls = [search_pat.format(name=comp_name, p=str(page + 1))]
                manager.put_urls_enqueue(batch_id, urls)
            if tree.cssselect('.table-search-list') and tree.cssselect('.tp2_tit a'):
                items = tree.cssselect('.table-search-list')
                for idx, i in enumerate(items):
                    if not i.xpath('.//*[@class=\"tp2_tit clear\"]/a/text()'):
                        continue
                    item = {}
                    item['name'] = i.xpath('.//*[@class=\"tp2_tit clear\"]/a/text()')[0]
                    # print(item['name'], file=log_file)
                    item['href'] = i.xpath('.//*[@class=\"tp2_tit clear\"]/a/@href')[0]
                    item['status'] = i.xpath('.//*[@class=\"tp5 text-center\"]/a/span/text()')[0]
                    item['key_num'] = item['href'].split('firm_')[1].split('.shtml')[0]
                    # print(item['key_num'], file=log_file)
                    urls.append(main_pat.format(key_num=item['key_num'], name=item['name']))
                    urls.append(invest_pat.format(key_num=item['key_num'], name=item['name'], p='1'))
                    dic['names'].append(item['name'])
            if not urls:
                return True
            manager.put_urls_enqueue(batch_id, urls)
            if not dic['names']:
                return True
            else:   # 不完全匹配时将search_name与前三个搜索结果存入json用作别名映射
                data = json.dumps(dic, encoding='utf-8', ensure_ascii=False)
                return process._cache.post(url, data)


        elif label == 'detail':     # 解析详情页面
            comp_name = urllib.unquote(m.group(2))
            all_info = parser.parse_detail(tree)
            all_info['name'] = comp_name
            all_info['source'] = url
            all_info['access_time'] = datetime.utcnow().isoformat()
            all_info = parser_patch(tree, all_info)
            all_info = reformat(all_info)
            data = json.dumps(all_info, encoding='utf-8', ensure_ascii=False)
            get_logger(batch_id, today_str, '/opt/service/log/').info(data)
            if not any([ i[1] for i in all_info['info']]):
                return False
            return process._cache.post(url, data)

        else:           # 解析投资页面
            comp_name = urllib.unquote(m.group(2))
            key_num = m.group(1)
            page = int(m.group(3))
            pages = tree.xpath(".//a[@id=\"ajaxpage\"]/text()")
            if '>' in pages:
                urls = [invest_pat.format(key_num=key_num, name=comp_name, p=str(page + 1))]
                manager.put_urls_enqueue(batch_id, urls)
            invest_dict = parse_company_investment(tree)
            if not invest_dict['sub_companies']:
                return True
            invest_dict['name'] = comp_name
            invest_dict['source'] = url
            invest_dict['access_time'] = datetime.utcnow().isoformat()
            data = json.dumps(invest_dict, encoding='utf-8', ensure_ascii=False)
            return process._cache.post(url, data)





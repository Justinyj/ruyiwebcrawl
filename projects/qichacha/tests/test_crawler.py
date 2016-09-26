#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# 企查查爬虫单元测试脚本, 分为三个部分
# test_searchpage 测试搜索页面解析是否正确
# test_detailpage 测试详情页面解析是否正确, 其中的parser_patch是在页面关于股东及主要人员部分改版后增加的补丁
# test_investpage 测试对外投资页面解析是否争取
# 注意使用时需更新cookie确保cookie有效


from __future__ import print_function, division

import sys
import os
import requests
import lxml.html
import re
import time
import json
import urlparse
from datetime import datetime

sys.path.append("..")
reload(sys)
sys.setdefaultencoding('utf-8')

from core.qiparser2 import QiParser
SITE = 'http://www.qichacha.com'

class QichachaTester(object):
    def __init__(self, gap, cookies):
        self.gap = gap
        self.cookies = cookies
        self.parser = QiParser()


    def crawl_searchpage(self, comp_name):
        url = "http://www.qichacha.com/search?key={}&index=0".format(comp_name)
        content = requests.get(url, cookies=self.cookies).text
        tree = lxml.html.fromstring(content.replace('<em>', '').replace('</em>', ''))


        print('getting items', comp_name)
        dic = { 'search_name': comp_name, 'names': [] }
        urls = []
        if tree.cssselect('.table-search-list') and tree.cssselect('.tp2_tit a'):
            items = tree.cssselect('.table-search-list')
            for idx, i in enumerate(items):
                if not i.xpath('.//*[@class=\"tp2_tit clear\"]/a/text()'):
                    continue
                item = {}
                item['name'] = i.xpath('.//*[@class=\"tp2_tit clear\"]/a/text()')[0]
                # print(item['name'])
                item['href'] = i.xpath('.//*[@class=\"tp2_tit clear\"]/a/@href')[0]
                item['status'] = i.xpath('.//*[@class=\"tp5 text-center\"]/a/span/text()')[0]
                item['key_num'] = item['href'].split('firm_')[1].split('.shtml')[0]
                # print(item['key_num'])
                if idx == 0 and comp_name == item['name']:
                    # print('appending', item['name'])
                    urls.append(urlparse.urljoin(SITE, item['href']))
                    break
                elif idx < 3:
                    urls.append(urlparse.urljoin(SITE, item['href']))
                    dic['names'].append(item['name'])
        if not urls:
            print("no result")
            return []
        print('----','URLS:',urls)
        if not dic['names']:
            return dic
        else:
            data = json.dumps(dic, encoding='utf-8', ensure_ascii=False)
            print('----projection:', data)
            return dic


    def test_detailpage(self):
        def reformat(info):
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

        url = "http://www.qichacha.com/company_getinfos?unique=1831925bc3d536bacb1fedda6ffe92fb&companyname=%E6%9D%AD%E5%B7%9E%E7%A8%B3%E5%81%A5%E9%92%99%E4%B8%9A%E6%9C%89%E9%99%90%E5%85%AC%E5%8F%B8&tab=base"
        content = requests.get(url, cookies=self.cookies).text
        tree = lxml.html.fromstring(content.replace('<em>', '').replace('</em>', ''))
        all_info = self.parser.parse_detail(tree)
        all_info['source'] = url
        all_info['access_time'] = datetime.utcnow().isoformat()
        all_info = parser_patch(tree, all_info)
        all_info = reformat(all_info)
        data = json.dumps(all_info, encoding='utf-8', ensure_ascii=False)
        print(data)
        if not all_info['shareholders'] or not all_info['executives']:
            print("[TestInfo]: Parser patch on shareholders or executives have expired!")
        if not any([ i[1] for i in all_info['info']]):
            print("[TestInfo]: Detail info tests Failed or Cookies have expired!")
        else:
            print("[TestInfo]: Detail info tests passed!")

    def test_searchpage(self):
        print("Testing exact match:")
        name_match = u"杭州稳健钙业有限公司"
        ret1 = self.crawl_searchpage(name_match)
        assert ret1 == { 'search_name': name_match, 'names': [] }, "[TestInfo]:Error in exact match"
        time.sleep(self.gap)

        print("Testing not match:")
        name_notmatch = u"杭州稳健钙业"
        ret2 = self.crawl_searchpage(name_notmatch)
        assert ret2 == { 'search_name': name_notmatch, 'names': [u"杭州稳健钙业有限公司"] }, "[TestInfo]:Error in not match"
        time.sleep(self.gap)

        print("Testing no result:")
        name_noresult = u"杭州稳健铁业"
        ret3 = self.crawl_searchpage(name_noresult)
        assert ret3 == [], "[TestInfo]:Error in no result"
        time.sleep(self.gap)
        print("[TestInfo]: Search page tests passed!")

    def test_investpage(self):
        def parse_company_investment(tree):
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
        url = "http://www.qichacha.com/company_getinfos?unique=fa31d50f310a6598e36ba97ed7864257&companyname=%E5%BB%BA%E5%BE%B7%E5%B8%82%E5%BB%BA%E4%B8%9A%E5%AE%B6%E7%BA%BA%E5%8E%82&tab=touzi"
        content = requests.get(url, cookies=self.cookies).text
        tree = lxml.html.fromstring(content.replace('<em>', '').replace('</em>', ''))
        invest_dict = parse_company_investment(tree)
        invest_dict['source'] = url
        invest_dict['access_time'] = datetime.utcnow().isoformat()
        data = json.dumps(invest_dict, encoding='utf-8', ensure_ascii=False)
        print(data)
        assert invest_dict['sub_companies'][0]['name'] == u"杭州稳健钙业有限公司", "[TestInfo]: Invest page test failed"
        print("[TestInfo]: Invest page tests passed!")




if __name__ == '__main__':
    
    cookies = { 1: "gr_user_id=520e5159-c317-427b-b729-32cfde21feea; _uab_collina=147330623190001355082584; _umdata=8CADC9282D9E757A1EE9201896AA893C63CF0FDD63F10F085690C94585F47D631F70FBBBE0D9C593E0FF065A56ADC299ABA63F2982D8433F9817B61CFC1BDCE5FADF904327FB8091CDD49BF635368D515C565B0FD655D63B292CFFA8779FBA83A67F1F22269B3CD3; PHPSESSID=4ogo08454m1310upuiqkm1a547; gr_session_id_9c1eb7420511f8b2=1f0d7896-a42f-4fbd-9b2d-36ff0441d61b; CNZZDATA1254842228=556867581-1473779583-http%253A%252F%252Fwww.qichacha.com%252F%7C1474909151"}

    tester = QichachaTester(5, cookies)
    tester.test_searchpage()
    tester.test_detailpage()
    tester.test_investpage()
        


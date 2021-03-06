#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import string
import re

class QiParser(object):
    def __init__(self):
        pass

    def parse_detail(self, tree):
        info = self.parse_basic_info(tree)
        massive_info = self.parse_massive_info(tree)
        massive_info.update({ 'info': info })
        return massive_info

    def parse_basic_info(self, html):
        info = {
            'unified_social_credit_code': None,
            'registration_id': None,
            'organization_code': None,
            'status': None,
            'business_type': None,
            'establish_date': None,
            'legal_person': None,
            'registered_capital': None,
            'begin': None,
            'end': None,
            'registration_authority': None,
            'approval_date': None,
            'address': None,
            'business_scope': None,
        }
        for li in html.cssselect('.base_info .company-base li'):
            label = li.cssselect('label')[0].text_content().strip()
            text = li.text_content().replace(label, '').strip()
            if label == u'注册号：':
                if not info['registration_id']:
                    info['registration_id'] = text
            elif label == u'统一社会信用代码：':
                if not info['unified_social_credit_code']:
                    info['unified_social_credit_code'] = text
            elif label == u'组织机构代码：':
               info['organization_code'] = text
            elif label == u'经营状态：':
                info['status'] = text
            elif label == u'公司类型：':
                info['business_type'] = text
            elif label == u'成立日期：':
                info['establish_date'] = text #datetime( *map(int, text.split('-')) )
            elif label == u'法定代表：':
                info['legal_person'] = text
            elif label == u'注册资本：':
                info['registered_capital'] = text
            elif label == u'营业期限：':
                info['begin'], info['end'] = map(lambda x: x.strip() if x.strip() != u'无固定期限' else None, text.split(u'至'))
                # info['begin'], info['end'] = map(lambda x: datetime(*map(int, x.strip().split('-'))) if x.strip() != u'无固定期限' else None, text.split(u'至'))
            elif label == u'登记机关：':
                info['registration_authority'] = text
            elif label == u'发照日期：':
                info['approval_date'] = text # datetime( *map(int, text.split('-')) )
            elif label == u'企业地址：':
                info['address'] = text.replace(u'查看地图', '').strip()
            elif label == u'经营范围：':
                info['business_scope'] = text
        return info


    def parse_massive_info(self, html):
        shareholders = []
        executives = []
        branches = []
        changes = []
        abnormals = []

        for section in html.cssselect('section.panel.clear'):
            section_title = section.cssselect('div.panel-heading .font-bold')[0].text_content().strip()
            if section_title == u"股东信息":
                for item in section.cssselect('div.panel-body > div.clear'):
                    shareholder = {
                        'name': None,
                        'role': None,
                        'link': None,
                        'subscribe_money': None,
                        'subscribe_time': None,
                        'actual_money': None,
                        'actual_time': None,
                    }
                    name = item.cssselect('a')[0]
                    shareholder['link'] = name.get('href').lstrip('/').rstrip('.shtml') if name.get('href').startswith('/firm_') else None
                    shareholder['name'] = name.text_content().strip()
                    shareholder['role'] = item.cssselect('.text-ellipsis')[0].text_content().strip()
                    for block in item.cssselect('.text-md'):
                        head, capital = map(string.strip, block.text_content().split(u'：'))
                        if head == u"认缴出资额":
                            shareholder['subscribe_money'] = capital
                        elif head == u"认缴出资时间":
                            shareholder['subscribe_time'] = capital
                        elif head == u"实缴出资额":
                            shareholder['actual_money'] = capital
                        elif head == u"实缴出资时间":
                            shareholder['actual_time'] = capital
                    shareholders.append(shareholder)
            elif section_title == u"主要人员":
                for item in section.cssselect('.col-md-3 > .panel > div.panel-body > div.clear'):
                    name = item.cssselect('a.text-lg')
                    if not name: continue
                    name = name[0].text_content().strip()
                    if not name: continue
                    if u'</' in name: continue # 保定京津医院
                    position = item.cssselect('small.text-muted')
                    position = position[0].text_content().strip() if position else None
                    position = None if (position and u'点评动态' in position) else position
                    executives.append({'name': name, 'position': position})
            elif section_title == u"分支机构":
                for item in section.cssselect('div.panel-body > div.clear > a'):
                    link = item.get('href')
                    link = link.lstrip('/').rstrip('.shtml')
                    name = item.text_content().strip()
                    branches.append( {'name': name, 'link': link} )
            elif section_title == u"变更记录":
                for item in section.cssselect('div.panel-body > div.clear'):
                    change = {
                        'project': None,
                        'change_time': None,
                        'before_change': None,
                        'after_change': None,
                    }
                    for block in item.cssselect('.text-muted'):
                        text = block.text_content().strip()
                        k, v = map(string.strip, text.split(u'：', 1))
                        if k == u'变更项目':
                            change['project'] = v
                        elif k == u'变更日期':
                            change['change_time'] = v
                        elif k == u'变更前':
                            change['before_change'] = v if v else None
                        elif k == u'变更后':
                            change['after_change'] = v
                    changes.append(change)
            elif section_title == u"经营异常":
                for item in section.cssselect('div.panel-body > div.clear'):
                    for block in item.cssselect('.text-muted'):
                        abnormal = {
                            'date': None,
                            'organs': None,
                            'reason': None,
                            'end_date': None,
                            'end_reason': None,
                        }
                        text = block.text_content().strip()
                        k, v = map(string.strip, text.split(u'：', 1))
                        if k == u'列入日期':
                            abnormal['date'] = v
                        elif k == u'作出决定机关':
                            abnormal['organs'] = v
                        elif k == u'列入经营异常名录原因':
                            abnormal['reason'] = v
                        elif k == u'移出日期':
                            abnormal['end_date'] = v
                        elif k == u'移出经营异常名录原因':
                            abnormal['end_reason'] = v
                    abnormals.append(abnormal)

        return {
            'shareholders': shareholders,
            'executives': executives,
            'branches': branches,
            'changes': changes,
            'abnormals': abnormals,
        }


    def parse_search_result(self, tree):
        summary_dict = {}
        if tree.cssselect('#options') and tree.cssselect('.list-group-item .name'):
            #new version after 2016-05-31
            for i in tree.cssselect('.list-group-item'):
                name = i.cssselect('.name')[0].text_content().strip()
                status = i.cssselect('.label')[0].text_content().strip()
                href = i.attrib['href']
                province, key_num = href.rstrip('.shtml').lstrip('/firm_').split('_', 1)
                if not name:
                    name = "NONAME-"+key_num
                summary_dict[name] = {
                    'name': name,
                    'status': status,
                    'key_num': key_num,
                    'href': href,
                    'province': province,
                }
        else:
            for i in tree.cssselect('#searchlist'):
                name = i.cssselect('.name')[0].text_content().strip()
                status = i.cssselect('.label')[0].text_content().strip()
                href = i.cssselect('.list-group-item')[0].attrib['href']
                key_num = href.rstrip('.shtml').rsplit('_', 1)[-1]
                summary_dict[name] = {
                    'name': name,
                    'status': status,
                    'key_num': key_num,
                    'href': href,
                }



        return summary_dict

    def parse_search_result_count(self, tree):
        ret = tree.cssselect('.panel-default .pull-left .text-danger')
        if ret:
            return int(ret[0].text_content().strip().replace("+",""))

        ret = tree.cssselect('.container .panel-default .pull-right span.text-danger')
        #print (ret,ret[0].text_content().strip())
        if ret:
            return int(ret[0].text_content().strip().replace("+",""))

        return 0

    def parse_company_investment(self, tree):
        invest_dict = {}
        for sub_company in tree.cssselect('.list-group a.list-group-item'):
            sub_name = sub_company.cssselect('span.clear .text-lg')[0].text_content().strip()
            href = sub_company.get('href')
            key_num = href.rsplit('_', 1)[-1]
            invest_dict[sub_name] = {
                'name': sub_name,
                'key_num': key_num,
                'href': href,
            }
        return invest_dict

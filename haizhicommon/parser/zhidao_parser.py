#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
import json

def parse_page_title(content):
    m = re.search('<title>(.*)</title>', content)
    if m:
        title = m.group(1)
        if u'_百度知道' not in title:
            if u'百度知道-信息提示' == title:
                return
            return
        title = re.sub(u'_百度知道', u'', title)
        return title
    return


def parse_q_time(content):
    m = re.search(
        '<em class="accuse-enter">.*\n*</ins>\n*(.*)\n*</span>', content)
    if m is None:
        return
    q_time = m.group(1)
    return q_time


def parse_q_content(content):
    q_content = ''
    m = re.search('accuse="qContent">(.*?)(</pre>|</div>)', content)
    n = re.search('accuse="qSupply">(.*?)(</pre>|</div>)', content)

    if m:
        q_content = m.group(1)
        q_content = re.sub('<.*?>', '\n', q_content)
        q_content = q_content.strip()
    if n:
        supply = n.group(1)
        q_content += supply

    if 'word-replace' in q_content:
        return

    return q_content


def parse_answer_ids(content):
    result = map(int, re.findall('id="answer-(\d+)', content))
    return result


def generate_question_json(qid, content):
    q_title = parse_page_title(content)
    if q_title is None:
        # print('未找到title或者页面不存在')
        return
    q_content = parse_q_content(content)
    if q_content is None:
        return

    q_time = parse_q_time(content)
    rids = parse_answer_ids(content)
    item = {
        'id': qid,
        'question': q_title,
        'question_content': q_content,
        'question_time': q_time,
        'answers': rids,
    }
    return item


def generate_answer_json(ans_content):
    content = json.loads(ans_content)
    return {
        'question_id': content[u'qid'],
        'answer_id': content[u'id'],
        'isBest': content[u'isBest'],
        'isHighQuality': content[u'isHighQuality'],
#        'isExcellent': content[u'isExcellent'],
        'isRecommend': content[u'isRecommend'],
#        'isSpecial': content[u'isSpecial'],
        'createTime': content[u'createTime'],
        'content': content[u'content'].encode('utf-8'),
        'valueNum': content[u'valueNum'],
        'valueBadNum': content[u'valueBadNum'],
    }


def zhidao_search_parse_qids(content):
    """
    :param content: content is unicode html string
    """
    ret = re.findall('href=\"(?:http://zhidao.baidu.com)?/question/(\d+).html', content)
    if ret:
        return ret[:1]
    return []

def zhidao_pick_questions(content):
    """
    :param content: content is unicode html string
    :return : a list consists of 1-2 question
    """
    dom = soupparser.fromstring(content)

    recommend = dom.xpath('//div[@id="wgt-autoask"]')
    result = []
    if recommend:
        url = recommend[0].xpath('.//a/@href')[0]
        q_id = re.findall('zhidao.baidu.com/question/(\d+).html', url)
        if q_id:
            HasRecommend = 1
            value_text = recommend[0].xpath('.//i[@class="i-agree"]/../text()')[1]
            recommend_approve = int(re.findall('(\d+)', value_text)[0])
            recommend_id = q_id[0]
            result.append(recommend_id)

    question_list = []
    first_q_id = None
    normal = dom.xpath('//dl[contains(@class,"dl")]')

    for node in normal:
        url = node.xpath('./dt/a/@href')
        q_id = re.findall('zhidao.baidu.com/question/(\d+).html', url[0])
        if not q_id:
            continue
        q_id = q_id[0]
        if not first_q_id:
            first_q_id = q_id
        node_text = node.xpath('.//i[@class="i-agree"]/../text()')
        if node_text:
            q_approve = int(node_text[1].strip())
            question_list.append((q_id, q_approve))

    max_approve = -1
    if question_list:
        question_list=sorted(question_list, key=lambda question: question[1])
        max_id,max_approve=question_list[-1]

    if result:
        #which means the recommend exists
        if max_approve>recommend_approve:
            result.append(max_id)
        return result
    else:
        return [first_q_id]

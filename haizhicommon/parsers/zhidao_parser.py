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
    result = re.findall('id="answer-(\d+)', content)
    return result


def parse_asker_username(content):
    m = re.search('a class="user-name" alog-action="qb-ask-uname" rel="nofollow" href="http://www.baidu.com/p/(.*?)\?from=zhidao" target="_blank">', content)
    if m:
        username = m.group(1)
        return username
    return

def generate_question_json(qid, content):
    q_title = parse_page_title(content)
    if q_title is None:
        # print('未找到title或者页面不存在')
        return
    q_content = parse_q_content(content)
    if q_content is None:
        return

    asker_username = parse_asker_username(content)
    q_time = parse_q_time(content)
    rids = parse_answer_ids(content)
    item = {
        'id': qid,
        'question': q_title,
        'question_content': q_content,
        'question_time': q_time,
        'asker_username': asker_username,
        'answer_ids': rids,
    }
    return item


def generate_answer_json(ans_content):
    content = json.loads(ans_content)
    return {
        'question_id': content[u'encode_qid'],
        'answer_id': str(content[u'id']),
        'is_best': content[u'isBest'],
        'is_highquality': content[u'isHighQuality'],
#        'is_excellent': content[u'isExcellent'],
        'is_recommend': content[u'isRecommend'],
#        'is_special': content[u'isSpecial'],
        'answer_time': content[u'createTime'],
        'content': content[u'content'].encode('utf-8'),
        'agreement': content[u'valueNum'],
        'disagreement': content[u'valueBadNum'],
    }


def zhidao_search_parse_qids(content):
    """
    :param content: content is unicode html string
    """
    ret = re.findall('href=\"(?:http://zhidao.baidu.com)?/question/(\d+).html', content)
    if ret:
        return ret[:1]
    return []

def zhidao_search_questions(content):
    """
    :param content: content is unicode html string
    :return : a list consists of 1-2 question

    说明：
    1.先检查推荐问题，如存在且合法则直接加入结果列表。 （合法指的是来源为百度知道网页，下同）
    2.再检查一般问题，将存在赞数的合法问题放入问题列表。
    3.对问题列表按照赞数进行排序，取得最高赞回答。
    4.最后处理结果：
    i.如果结果中有推荐问题，当最高赞问题赞数高于推荐问题则加入，反之丢弃。
    ii.如果结果中没有推荐问题，直接加入最高赞问题。
    iii.如果第二步中不存在最高赞问题，即所有合法问题都无赞，则加入原始页面中第一个合法问题。
    
    """
    import lxml.html
    dom = lxml.html.fromstring(content)

    recommend = dom.xpath('//div[@id="wgt-autoask"]')
    result = []
    recommend_approve = 0
    if recommend:
        url = recommend[0].xpath('.//a/@href')[0]
        q_id = re.findall('zhidao.baidu.com/question/(\d+).html', url)
        if q_id:
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

    if max_approve>recommend_approve:
        result.append(max_id)
        return result
    else:
        return [first_q_id]

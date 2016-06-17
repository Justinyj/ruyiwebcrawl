# -*- coding: utf-8 -*-
import re
import json
import os
import time
import sys
import requests
reload(sys)
sys.setdefaultencoding("utf-8")
import lxml.html

'''
req = requests.get(
    'http://www.zybang.com/question/a8a5c891d55bb988c85ec224245057c9.html')
req.encoding = 'utf-8'
content = req.text
'''

def parse_q_id(url):
    # 网页中无法找到qid
    q_id = re.findall('zybang.com/question/(.*).html', url)
    if q_id:
        return q_id[0]


def get_question_dict(dom):
    texts = dom.xpath('.//span/text()')
    question = ''.join(texts[0:-2])
    asker_username = texts[-2]
    question_time = texts[-1]
    question = {
        'question': question,
        'asker_username': asker_username,
        'question_time': question_time,
    }
    return question


def parse_question(dom):
    question_node = dom.xpath('//dl[contains(@class,"qb_wgt-question")]/dd')
    question = None
    if question_node:
        question_node = question_node[0]
        question = get_question_dict(question_node)
    return question


def parse_zuoyebang(content):
    dom = lxml.html.fromstring(content)
    question_dict = parse_question(dom)
    best_answer = dom.xpath('//dl[@id="good-answer"]/dd/span//text()')
    best_answer_content = ''.join(best_answer)

    normal_nodes = dom.xpath('(//dd[@class="answer"]|//dd[@class="manswer"])')
    answer_nodes = []
    for index in range(len(normal_nodes)):
        # 对于有展开项的文本，answer是部分答案，manswer是全部答案，两者并列存在
        current_node = normal_nodes[index]
        a_class = current_node.xpath('./@class')[0]
        if a_class == 'manswer':
            answer_nodes.pop()
        answer_nodes.append(current_node)
    answer_nodes = answer_nodes[:3]
    answer_content = []
    for answer in answer_nodes:
        m = answer.xpath('./span/text()')[0]
        answer_content.append(m)

    result = {
            'answers': best_answer_content,  # for best answer
            'answer_list': answer_content,
            'question_content': None,
            'id': None,
            'parse_time': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
            'answer_ids': None,
        }

    result.update(question_dict)
    retjson = json.dumps(result, ensure_ascii=False)
    return retjson
#print  parse_zuoyebang(content)

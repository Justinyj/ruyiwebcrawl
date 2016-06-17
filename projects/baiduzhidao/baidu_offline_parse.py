# -*- coding: utf-8 -*-
import re
import json
import os
import time
import sys
reload(sys)
sys.setdefaultencoding("utf-8")
file_name = 'result/zhidao0614'
import scrapy
from parsers.zhidao_parser import *
replace_count=0




def parse_q_id(content):
    q_id = re.search(
        'rel="canonical" href="http://zhidao.baidu.com/question/(\d+).html"', content)
    if q_id:
        question_id = q_id.group(1)
        return question_id
    return



def parse_recommend(response):
    text = response.xpath('//pre[contains(@id,"recommend-content")]/text()')
    if not text:
        return None
    content = ''
    text = text.extract()
    for i in text:
        content += (i.encode('utf-8'))
    r_id = response.xpath(
        '//div[contains(@class,"wgt-recommend")]/@id').extract()[0]
    try:
        up = response.xpath(
        '//div[contains(@class,"wgt-recommend")]//span[@alog-action="qb-zan-btnrecombox"]/@data-evaluate')[0].extract()
    except:
        up=None
    try:
        down = response.xpath(
        '//div[contains(@class,"wgt-recommend")]//span[@alog-action="qb-evaluate-outer"]/@data-evaluate')[0].extract()
    except:
        down=None
    answer_time = response.xpath(
        '//div[contains(@class,"wgt-recommend")]//span[@class="grid-r f-aid pos-time mt-15"]/text()')[0].extract()
    answer = {
        'answer_id': r_id.replace(u'recommend-answer-', ''),
        'isBest': 0,
        'isHighQuality': 0,
        'isRecommend': 1,
        'createTime': answer_time,
        'content': content,
        'valueNum': up,
        'valueBadNum': down,
    }
    return answer


def parse_quality(response):
    text = response.xpath(
        '//div[@class="quality-content-detail content"]//text()')
    if not text:
        return
    text = text.extract()
    content = ''
    for i in text:
        content += i
    m = re.search(
        'div class="answer-share-widget answer-share-(\d+?) quality-answer-share', response.body)
    r_id = m.group(1)
    answer_time = response.xpath(
        '//span[@class="reply-time grid-r"]/text()').extract()

    answer = {
        'answer_id': r_id,
        'isBest': 0,
        'isHighQuality': 1,
        'isRecommend': 0,
        'createTime': answer_time,
        'content' : content,
        'valueNum': None,
        'valueBadNum': None,
    }
    return answer


def parse_best(response):
    text = response.xpath('//pre[@class="best-text mb-10"]//text()')
    if not text:
        return
    content = ''
    text = text.extract()
    for i in text:
        content += (i.encode('utf-8'))
    r_id = response.xpath(
        '//div[contains(@class,"wgt-best mod-shadow")]/@id').extract()[0]
    up = response.xpath(
        '//div[contains(@class,"wgt-best mod-shadow")]//span[@alog-action="qb-zan-btnbestbox"]/@data-evaluate')
    if up:
        up=up[0].extract()
    else:
        up=0
    down = response.xpath(
        '//div[contains(@class,"wgt-best mod-shadow")]//span[@alog-action="qb-evaluate-outer"]/@data-evaluate')
    if down:
        down=down[0].extract()
    else:
        down=0
    answer_time = response.xpath(
        '//div[contains(@class,"wgt-best mod-shadow")]//span[@class="grid-r f-aid pos-time mt-20"]/text()')
    if answer_time:
        answer_time=answer_time[0].extract()
    else:
        answer_time=0
    answer = {
        'answer_id': r_id.replace('best-answer-', ''),
        'isBest': 1,
        'isHighQuality': 0,
        'isRecommend': 0,
        'createTime': answer_time,
        'content': content,
        'valueNum': up,
        'valueBadNum': down,
    }
    return answer


def parse(response):
    content = response.body
    if ('word-replace') in content:
        global replace_count
        replace_count += 1
        return
    s = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
    q_id = parse_q_id(content)
    if not q_id:
        return
    answer_list = []
    best_answer=''
    answer = parse_best(response)
    if answer:
        answer_list.append(answer)
        best_answer=answer['content']

    answer = parse_recommend(response)
    if answer:
        answer_list.append(answer)

    answer = parse_quality(response)
    if answer:
        answer_list.append(answer)

    if len(answer_list) == 0:
        return
    item = {
        'question': parse_page_title(content),
        'id': q_id,
        'question_content': parse_q_content(content),
        'answers':best_answer,
        'ask_username': parse_asker_username(content),
        'question_time': parse_q_time(content),
        'parse_time': s,
        'answer_list': answer_list,
    }

    x = json.dumps(item, ensure_ascii=False)
    return x

def traverseDirByListdir(path):
    path = os.path.expanduser(path)
    f = open(file_name, 'w')
    for p in os.listdir(path):
        if p[:4] != 'mres':
            continue
        json = ''
        with open(p, 'r') as file:
            while(1):
                content = file.readline()
                if not content:
                    break
                response = scrapy.http.response.html.HtmlResponse('123', encoding='utf-8', body=content)
                json = parse(response)
                if not json:
                    continue
                f.write(json + '\n')
    f.close()

pa = os.path.abspath(os.path.dirname(__file__))
#traverseDirByListdir(pa)
#f=open('log','w')
#f.write(str(replace_count))
#f.close()

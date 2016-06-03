#-*- coding:utf-8 -*-
import re
import json
import os
import sys
import traceback
import requests
import sys
import base64
import collections
import chardet
import logging
import time

reload(sys)
sys.setdefaultencoding("utf-8")

VERSION = "201605"
DATA_PATH = os.path.abspath(os.path.dirname(__file__)).replace("/projects/", "/local/") 
LINK_RAW_FILE = DATA_PATH + "/link_question_all.txt"
OUTPUT_ES_FILE = DATA_PATH + "/baiduzhidao.{}.esdata".format(VERSION)
FAIL_IDS_FILE = DATA_PATH + "/fail_ids.txt"
SUCCESS_IDS_FILE = DATA_PATH + "/success_ids.txt"
BATCH_ID_FILE = DATA_PATH + "/batch_id_record.txt"
LOG_FILE = DATA_PATH + "/log"
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG)

counter = collections.Counter()

def crawl_url(url):
    try:
        api_url = 'http://106.75.6.152:8002/v1/fetch/get/{}'
        
        b64url = base64.urlsafe_b64encode(url)
        fetch_url = api_url.format(b64url)
        batch_id = get_batch_id()
        data = {'batch_id': batch_id, 'gap': 2, 'encode': 'gb18030', 'header': {'Host': 'zhidao.baidu.com', 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.63 Safari/537.36', 'Connection': 'keep-alive', 'Cache-Control': 'max-age=0', 'Upgrade-Insecure-Requests': '1'}}
        r = requests.get(fetch_url, data=json.dumps(data))
        
        assert r.status_code == 200
        content = r.json()[u'source'].encode("utf-8")
        return content
    except:
        traceback.print_exc()
        print "爬取出错：{}".format(url)
        logging.debug("爬取出错：{}".format(url))
        return None
    
def get_batch_id():
    with open(BATCH_ID_FILE, "r") as f:
        lines = f.readlines()
        if len(lines) > 0:
            return lines[0].strip()

def parse(content, q_id):
    title = parse_title(content)
    if title is None or '信息提示' in title:
        print '未找到title或者页面不存在,q_id:{}'.format(q_id)
        logging.debug('未找到title或者页面不存在,q_id:{}'.format(q_id))
        counter['invalid page']+=1
        return None
    
    q_content = parse_q_content(content)
    username = parse_username(content)
    q_time = parse_q_time(content)
    crawl_time = time.strftime('%Y-%m-%d %H:%M', time.localtime(time.time()))
    
    answer_ids = parse_answer_ids(content)
    answers_result = []
    for answer_id in answer_ids:
        answer_result = get_answer(q_id, answer_id)
        if answer_result is not None:
            answers_result.append(answer_result)
    if len(answers_result) == 0:
        print '该问题没有回答，q_id:{}'.format(q_id)
        logging.debug('该问题没有回答，q_id:{}'.format(q_id))
        counter['no answer']+=1
        return None
    answers = answers_result[0].get('contentText', '')
    if answers == '':
        print '百度答案API中contentText为空,q_id:{},answer_id:{}'.format(q_id, answer_ids[0])
        logging.debug('百度答案API中contentText为空,q_id:{},answer_id:{}'.format(q_id, answer_ids[0]))
        counter['contentText is None']+=1
        return None
    meta_data = answers_result[0]
    
    item = {
            'id': "baiduzhidao:{}".format(q_id),
            'question': title,
            'q_content': q_content,
            'username': username,
            'q_time': q_time,
            'crawl_time': crawl_time,
            'answers': answers,
            'meta_data': meta_data,
            'all_answers': answers_result
            }
    return item
    
def parse_title(content):
    m = re.search("<title>(.*)</title>", content)
    if m is not None:
        title = m.group(1)
        title = re.sub("_百度知道", "", title)
        return title
    return None

def parse_q_content(content):
    m = re.search('accuse="qContent">(.*)</pre>', content)
    if m is not None:
        q_content = m.group(1)
        q_content = re.sub("<.*?>", "\n", q_content)
        q_content = q_content.strip()
        return q_content
    return None

def parse_username(content):
    m = re.search('<a alog-action="qb-username".*target="_blank">\n*(.*)\n*</a>', content)
    if m is not None:
        username = m.group(1)
        return username
    return None

def parse_q_time(content):
    m = re.search('<em class="accuse-enter">.*\n*</ins>\n*(.*)\n*</span>', content)
    if m is not None:
        q_time = m.group(1)
        return q_time
    return None

def parse_answer_ids(content):
    ids = []
    m = re.search('id="best-content-(\d+)"', content)
    if m is not None:
        id = m.group(1)
        ids.append(id)
    other_ids = re.findall('id="answer-content-(\d+)"', content)
    ids.extend(other_ids)
    return ids

def get_answer(q_id, answer_id):
    url = 'http://zhidao.baidu.com/question/api/mini?qid={}&rid={}&tag=timeliness'.format(q_id, answer_id)
    content = crawl_url(url)
    try:
        answer = json.loads(content)
        return answer
    except:
        traceback.print_exc()
        print '获取答案出错'
        print 'q_id:', q_id
        print 'answer_id', answer_id
        logging.debug('获取答案出错,q_id:{},answer_id:{}'.format(q_id, answer_id))
        return None


def run():
    items = []
    fail_ids = []
    success_ids = read_success_ids()
    
    urls = read_urls()
    for url in urls:
        counter['url']+=1
        m = re.search("\d+", url)
        if m is not None:
            q_id = m.group(0)
            counter['legal url']+=1
            if q_id in success_ids:
                continue
            
            content = crawl_url(url)
            if content is None:
                fail_ids.append(q_id)
                counter['fail']+=1
                continue
            
            item = parse(content, q_id)
            if item is None:
                fail_ids.append(q_id)
                counter['fail']+=1
            else:
                items.append(item)
                counter['success']+=1
                success_ids.append(q_id)
                if counter['success'] % 100 ==0:
                    write_es(items)
                    write_success_ids(success_ids)
                    items = []
                    success_ids = []
        else:
            print '错误的url:{}'.format(url)
            logging.debug('错误的url:{}'.format(url))
            counter['illegal url']+=1
        print counter
    
    write_es(items)
    write_success_ids(success_ids)
    write_fail_ids(fail_ids)
    
def read_urls():
    urls = []
    with open(LINK_RAW_FILE, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line != '':
                urls.append(line)
    return urls

def write_es(items):
    with open(OUTPUT_ES_FILE, "a") as out:
        for item in items:
            out.write(json.dumps(item, ensure_ascii=False))
            out.write("\n")
            
def write_fail_ids(fail_ids):
    with open(FAIL_IDS_FILE, "w") as out:
        out.write("\n".join(fail_ids))

def write_success_ids(success_ids):
    with open(SUCCESS_IDS_FILE, "w") as out:
        out.write("\n".join(success_ids))
        
def read_success_ids():
    success_ids = []
    with open(SUCCESS_IDS_FILE, "r") as f:
        for line in f.readlines():
            line = line.strip()
            if line != '':
                success_ids.append(line)
                
    return success_ids
        
if __name__ =="__main__":
    run()

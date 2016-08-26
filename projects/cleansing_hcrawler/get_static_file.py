# coding: utf-8


# 脚本介绍：根据names.txt 进行统计分类，之后依靠人工标注，通过另一个脚本file_to_json调用以生成映射json
import csv
import json
from mongoengine import *
from hcrawler_models import Hprice, Hentity
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
DB = 'hcrawler'
connect(db = DB, host='localhost:27017', username = 'hcrawler', password = 'f#d1p9c')
counter = 0
ok_list = []
candidate_list = []
bad_list = []
only_one_list = []

def judge_by_desc(desc):
    words_list = {
        '游戏' : -100,
        '电影' : -100,
        '本草'  :   50,
        '学名'  :  10,
        '中药名':  100,
        '中药材':  100,
        '纲目'  :   10,
        '熔点'  :   10,
        '药'    : 10,
        '化合物' :50,
        '分布'   :10,
        '化学式' : 10,
    }
    score = 0
    if not desc:
        return 0
    for word, weight in words_list.iteritems():
        if word in desc:
            score += weight
    return score


def judge_by_sameas(sameas):
    words_list = {
        '中药': 100,
        '人物': -100,
        '电影' : -100,
        '电视':-100,
        '演'   : -100,
        '植物' : 50,
        '小说' : -100,
        '草药'   : 50,
    }
    score = 0
    if not sameas:
        return 0
    for word, weight in words_list.iteritems():
        if word in sameas:
            score += weight
    return score

def allocate_tag_by_score(tags_with_scores):
    #sort
    exist_ok = 0
    if len(tags_with_scores) == 1:  #长度为1，没有别的选择，直接分类
        only_one_list.append(tags_with_scores[0][0])
        return

    tags_with_scores = sorted(tags_with_scores, key = lambda item:item[1], reverse = True)
    for tag, score in tags_with_scores:
        if score >= 100:  
            ok_list.append(tag)
            exist_ok  = 1
            continue # 接下来可能还会有合理实体，所以不用return

        elif exist_ok:
            return  #如果存在合理实体，则其他都丢弃

        if score > -100:    #属于分数既不高也不低的实体，加入candidate_list
            candidate_list.append(tag)
        else:
            bad_list.append(tag)  #说明这是个不合适的实体，丢弃



def deal_with(name):
    global counter
    ret_list = Hentity.objects.filter(Q(s_label=name) |  Q(alias__in=[name]))
    tags_with_scores = []

    for candi in ret_list:
        desc = candi.description
        sameas = candi.sameas[0]
        score = judge_by_desc(desc) + judge_by_sameas(sameas)
        tag = [name, score, candi.s_label, candi.nid, ','.join(candi.alias), sameas, desc]
        tags_with_scores.append([tag, score])
    counter += len(tags_with_scores)
    allocate_tag_by_score(tags_with_scores)


def write_to_file(filename, content_list):
    with open(filename, 'w') as f:
        writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(['所查名字', '评分', '实体名', 'nid', '别名', 'sameas', '描述'])
        for name in  content_list:    
            writer.writerow(name)


if __name__ == '__main__':
    with open('names.txt', 'r') as f:
        for line in f:
            name = line.strip() #mapper.get(raw, raw)
            deal_with(name)
    
    print counter
    write_to_file('candidate.csv', candidate_list)
    write_to_file('ok.csv', ok_list)
    write_to_file('bad.csv', bad_list)
    write_to_file('onlyone.csv', only_one_list)
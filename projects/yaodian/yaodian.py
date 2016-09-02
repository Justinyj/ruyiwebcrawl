#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>

import requests
from lxml import etree
import re
import time
import json
import codecs
import sys
import hashlib
from datetime import datetime

reload(sys)  
sys.setdefaultencoding('utf8')

SITE = "http://www.yaobiaozhun.com/yd2015/"
url = "http://www.yaobiaozhun.com/yd2015/view.php?v=txt&id={}"



def has_key(info, key):
    for item in info:
        if item.get(key, None):
            return True
    return False

def parse(detail, index, lurl):
    page = etree.HTML(detail.text.replace('<sub>', '').replace('</sub>', ''))
    name = page.xpath("//*[@id=\"article_info\"]/h1/text()")[0]
    name_eng = page.xpath("//*[@class=\"cms_list\"]/pre/center[3]/b/text()")[0] if page.xpath("//*[@id=\"wrap\"]/div[3]/div[2]/div[3]/pre/center[3]/b/text()") else ''
    print name, index
    content = ''.join(page.xpath('//div[@id="content_text"]//text()')).rstrip()

    basic = ''
    m = re.search(u'(.*)\n', content)
    firstline =  m.group(1).strip()
    basic = '' if '【' in firstline else firstline

    print basic
    # if not name or not content:
    #     print i, 'not captured'
    # print json.dumps(content, encoding='utf-8', ensure_ascii=False)
    info  = []
    info.append({u'实体定义': basic})
    info.append({u'英文名': name_eng})

    content += u'\n 【' # 为了让最后一个字段成功匹配
    for i in re.findall(u'【([^】]+?)】((.|\s)+?)(?= 【)', content):
        key = i[0]
        value = i[1]
        if not has_key(info, key):
            info.append({key: value.strip()}) #  防止http://www.yaobiaozhun.com/yd2015/view.php?v=txt&id=356 倒数第五行的情况出现

    data = {
        u'name'  : name,
        u'source': lurl,
        u'info'  : info, 
        u'access_time' : datetime.utcnow().isoformat(),
    }
    if info == []:
        with open('failed.log', 'a') as f:
            f.write(lurl + '\n')
    return data

def run():
    for i in range(1, 2579):  # 药典一部里有2158种药材
        lurl = url.format(str(i))
        time.sleep(1)
        if i % 100 == 0:
            time.sleep(5)
        detail = requests.get(lurl)
        # print detail.text
    
        data = parse(detail, i, lurl)
        filename = hashlib.sha1(lurl).hexdigest()
        # print json.dumps(data, encoding='utf-8', ensure_ascii=False)
        with codecs.open(filename, 'w', encoding='utf-8') as file:
            file.write(json.dumps(data, encoding='utf-8', ensure_ascii=False))  

if __name__ == '__main__':
    run()
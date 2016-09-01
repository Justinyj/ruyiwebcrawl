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

for i in range(1, 2159):  # 药典一部里有2158种药材
    lurl = url.format(str(i))
    time.sleep(1)
    if i % 100 == 0:
        time.sleep(5)
    detail = requests.get(lurl)
    # print detail.text
    data = {}
    page = etree.HTML(detail.text.replace('<sub>', '').replace('</sub>', ''))
    name = page.xpath("//*[@id=\"article_info\"]/h1/text()")[0]
    content = [ c.strip() for c in page.xpath("//*[@id=\"content_text\"]/text()")[0].split('\r\n') ]
    name_eng = page.xpath("//*[@class=\"cms_list\"]/pre/center[3]/b/text()")[0] if page.xpath("//*[@id=\"wrap\"]/div[3]/div[2]/div[3]/pre/center[3]/b/text()") else ''
    print name, i
    j = 0
    data['basic'] = ''
    for c in content:
        m = re.compile(r'【.+?】').match(c.encode('utf-8'))
        if not m:
            data['basic'] += c
            j += 1
        else:
            break
    print data['basic'], j
    # if not name or not content:
    #     print i, 'not captured'
    # print json.dumps(content, encoding='utf-8', ensure_ascii=False)
    data['source'] = lurl
    data['name'] = name
    
    data['name_eng'] = name_eng
    data['access_time'] = datetime.utcnow().isoformat()
    for info in content[j:]:
        m = re.compile(r'【.+?】').match(info.encode('utf-8'))
        if m:
            prop = m.group(0)[3:-3]
            cleaned = re.sub(r'【.+?】', '', info.encode('utf-8'))
            data[prop] = cleaned
        else:
            data[prop] += '\n' + info.encode('utf-8')
    filename = hashlib.sha1(lurl).hexdigest()
    # print filename
    # print json.dumps(data, encoding='utf-8', ensure_ascii=False)
    with codecs.open(filename, 'w', encoding='utf-8') as file:
        file.write(json.dumps(data, encoding='utf-8', ensure_ascii=False))

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# 此脚本用于爬取蒲标网上的中国药典一部文字内容，存入当前路径下的'yaodian2015.json'文件
import requests
from lxml import etree
import re
import time
import json
import codecs


url = "http://www.yaobiaozhun.com/yd2015/view.php?v=txt&id={}"

for i in range(1, 2159):
    time.sleep(1)
    detail = requests.get(url.format(str(i)))
    # print detail.text
    data = {}
    page = etree.HTML(detail.text.replace('<sub>', '').replace('</sub>', ''))
    name = page.xpath("//*[@id=\"wrap\"]/div[3]/div[2]/div[3]/pre/center[1]/b/text()")[0]
    pinyin = page.xpath("//*[@id=\"wrap\"]/div[3]/div[2]/div[3]/pre/center[2]/b/text()")[0] if page.xpath("//*[@id=\"wrap\"]/div[3]/div[2]/div[3]/pre/center[2]/b/text()") else ''
    content = page.xpath("//*[@id=\"wrap\"]/div[3]/div[2]/div[3]/pre/text()[1]")[0]
    name_eng = page.xpath("//*[@id=\"wrap\"]/div[3]/div[2]/div[3]/pre/center[3]/b/text()")[0] if page.xpath("//*[@id=\"wrap\"]/div[3]/div[2]/div[3]/pre/center[3]/b/text()") else ''
    print name, i
    if not name or not content:
        print i, 'not captured'
    data['name'] = name
    data['pinyin'] = pinyin
    data['content'] = content
    data['name_eng'] = name_eng
    with codecs.open('yaodian2015.json', 'a', encoding='utf-8') as file:
        file.write(json.dumps(data, encoding='utf-8', ensure_ascii=False) + '\n')
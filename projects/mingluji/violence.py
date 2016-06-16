# -*- coding: utf-8 -*-
import requests
import lxml.html
import re
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class MingluSpider(object):

    def __init__(self):
        self.out = open('comany_name.txt', 'a')
        self.url_file = open('out.txt', 'r')
        f = open('record.txt', 'r')
        record = f.readline().strip()
        f.close()
        if record == '':
            record = 0
        record = int(record)
        self.record = record

    def update_record(self):
        self.record+=1
        if self.record % 100==0:
        	print self.record
        f = open('record.txt', 'w')
        f.write(str(self.record))
        f.close()

    def GetPosition(self):
        for _ in range(self.record):
            self.url_file.readline()
    def get_name(self,content):
        dom=lxml.html.fromstring(content)
        name=dom.xpath('//span[@class="field-content"]//text()')
        return name
    def traversal(self):
        while 1:
            url = self.url_file.readline().strip()
            if not url:
                break
            content=requests.get(url).text
            name=self.get_name(content)
            if not name :
                if 'block-gongshang-mingluji-com-province-industry' not in content:
                    print url
                    print 'ERROR PAGE!!'
                    return
            for i in name:
                self.out.write(i+'\n')
            self.update_record()

obj=MingluSpider()
obj.traversal()

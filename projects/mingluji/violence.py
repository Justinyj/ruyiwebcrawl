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
        self.out = open('company_name.txt', 'a')
        self.url_file = open('all_urls.txt', 'r')
        f = open('persistent_outtxt_lineno.txt', 'r')
        record = f.readline().strip()
        f.close()
        if record == '':
            record = 0
        record = int(record)
        self.record = record

    def update_record(self):
        self.record += 1
        if self.record % 100 == 0:
            print self.record
        f = open('persistent_outtxt_lineno.txt', 'w')
        f.write(str(self.record))
        f.close()


    def GetPosition(self):
        for _ in range(self.record):
            self.url_file.readline()


    def get_name_with_re(self, content):
        m = re.findall(
            '<span class="field-content"><a href="(.*?)">(.*?)</a></span>', content)
        res = [i[1] for i in m]
        return res


    def get_name_with_xpath(self, content):
        dom = lxml.html.fromstring(content)
        name = dom.xpath('//span[@class="field-content"]//text()')
        return name


    def traversal(self):
        self.GetPosition()
        while 1:
            url = self.url_file.readline().strip()
            if not url:
                return
            try:
                content = requests.get(url).text
            except:
                content = requests.get(url).text
                print url
                print 'ERROR IN GETTING CONTENT!!'
                self.update_record()
                continue
            name = self.get_name(content)
            if not name:
                if 'block-gongshang-mingluji-com-province-industry' not in content:
                    print url
                    print 'ERROR PAGE!!'
                    return
                continue
            for i in name:
                self.out.write(i + '\n')
            self.update_record()


obj = MingluSpider()
obj.traversal()

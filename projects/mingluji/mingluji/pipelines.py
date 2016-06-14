# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs


class MinglujiPipeline(object):
    def __init__(self):
        self.file = codecs.open('mingluji_urls.txt', 'w')
        self.count=0
    def process_item(self, item, spider):

        line=json.dumps(dict(item),ensure_ascii=False)+"\n"
        self.file.write(line)
        self.count+=item['num']
        print self.count
        return item



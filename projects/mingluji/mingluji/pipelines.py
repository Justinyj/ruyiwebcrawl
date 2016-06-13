# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs


class MinglujiPipeline(object):
    def __init__(self):
        self.item_count=0
        self.file_count=0
        self.file = codecs.open(str(self.file_count), 'w')
    def process_item(self, item, spider):
        self.item_count+=1
        if (self.item_count>50000):
        	self.item_count=0
        	self.file_count+=1
        	self.file.close()
        	self.file = codecs.open(str(self.file_count), 'w')
        	print  'file up to{}'.format(file_count)

        line=json.dumps(dict(item),ensure_ascii=False)+"\n"
        self.file.write(line)
        return item

# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import codecs

class DongfangcaifuPipeline(object):
    def __init__(self):
        self.file = codecs.open('url_per_notice.txt', 'w')
    def process_item(self, item, spider):
    	'''
        line=json.dumps(dict(item),ensure_ascii=False)+"\n"
        '''
        line=item['url']
        self.file.write(line+'\n')
        return item

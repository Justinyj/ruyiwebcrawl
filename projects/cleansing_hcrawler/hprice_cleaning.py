#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import sys
import collections
from datetime import datetime
import re
reload(sys)
sys.setdefaultencoding('utf-8')
from to_es import sendto_es


class HpriceCleansing(object):
    def __init__(self, dir_name, debug = False):
        self.dir_name = dir_name
        self.source_files_path = None
        self.counter = 0
        self.jsons = []
        self.myset  = set()
        self.debug = debug

        with open ('map.json', 'r')  as f:
            self.nameMapper = json.load(f)


    def set_source_files_path(self):
        dir_path =  '/data/hproject/2016/' + self.dir_name
        
        if os.path.isdir(dir_path):  
            file_list = os.listdir(dir_path)
            self.source_files_path = [dir_path + '/' + file for file in file_list]
        else:
            raise IOError('no such directory: {}'.format(dir_path))


    def parse_single_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                if line.strip():

                    item = json.loads(line.strip())
                    self.parse_single_item(item)
        sendto_es(self.jsons)
        self.counter = 0
        self.jsons = []


    def parse_single_item(self, item):
        pass


    def init_item_schema(self):
        item_suit_schema = {
                    'productGrade' :            None,   # 产品等级
                    'priceCurrency' :           None,   # 价格货币，命名规则使用iso-4217
                    'createdTime' :             None,   # 生成时间
                    'confidence' :              None,   # 
                    'productPlaceOfOrigin' :    None,   # 原产地
                    'maxPrice' :                None,   # 最高价
                    'seller' :                  None,   # 销售
                    'source' :                  None,   # 数据源url
                    'tags' :                    None,   # 标签   
                    'productionYear' :          None,   # 生产年限
                    'unitText' :                None,   # 价格单位
                    'mainEntityOfPage' :        None,   # 
                    'mainEntityOfPage_raw' :    None,   # 
                    'sellerMarket' :            None,   # 报送单位(在中华粮网里出现，是各地市场)
                    'minPrice' :                None,   # 最低价
                    'productSpecification' :    None,   # 产品规格
                    'priceType' :               None,   # 价格类型
                    'description' :             None,   # 产品描述
                    'validMonth'  :             None,
                }
        
        return item_suit_schema

    def clean_item_schema(self, schema):  
    #主要负责实体映射，抽取domain，生成tags,name，以及加入统计字段到set中
    #换言之，所有需要组合，二次生成的字段，都在这个方法里完成。原则上子类的方法中填写的都是直接可以从原数据直接获得。
    #由于kmzy的name结构不一样，所以在这生成后的是错误类型，要在子类里覆盖一下。
        v = schema['mainEntityOfPage_raw']
        schema['mainEntityOfPage'] = self.nameMapper.get(v, v)
        if self.debug and schema['mainEntityOfPage'] != v:
           print (schema['mainEntityOfPage'].encode('utf-8'))

        v = schema['source']
        schema['sourceDomainName'] = re.findall('http://(.*?)/', v)[0]
        schema['tags'] = [ schema['sourceDomainName'] , schema['mainEntityOfPage'] ]
        schema['name'] = ('{}_{}_{}_{}').format(schema['mainEntityOfPage_raw'], schema['priceType'], schema['sellerMarket'], schema['productGrade'])
        self.myset.add( '{},{},{}'.format(schema['sourceDomainName'], schema, schema['name']))

    def clean_item_data(self, schema):
        #负责清洗时间，并加上处理时间数据
        v = schema['validDate']
        if len(v) == 7:
            schema['validMonth'] = v
        schema['createdTime'] = datetime.today().isoformat()

    def run(self):
        self.set_source_files_path()
        for file_path in self.source_files_path:
            self.parse_single_file(file_path)
        with open('out.txt','a') as f:
            for i in self.myset:
                f.write(i+'\n')

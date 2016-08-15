#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from to_es import sendto_es


class hjson_extractor(object):
    def __init__(self, dir_name):
        self.dir_name = dir_name
        self.source_files_path = None
        self.counter = 0
        self.jsons = []

    def set_source_files_path(self):
        dir_path =  '/data' + '/' + self.dir_name
        if os.path.isdir(dir_path):  
            file_list = os.listdir(dir_path)
            self.source_files_path = [dir_path + '/' + file for file in file_list]
        else:
            raise IOError('no such directory: {}'.format(dir_path))


    def parse_single_file(self, file_path):
        with open(file_path, 'r') as file:
            for line in file:
                item = json.loads(line)
                item_suit_schema = self.parse_single_item(item)

                self.jsons.append(item_suit_schema)
                self.counter += 1
                if self.counter == 1000:
                    # sendto_es(jsons)
                    self.counter = 0
                    self.jsons = []

    def parse_single_item(self, item):
            # 时间关系，这里暂时设成父类方法为分析药通网，未来可以调整优化
            # 药通网的price_history是一个字典，key为日期，value为价格
            item_suit_schema = {
                    'name' : item[u'name'],                         # 品种
                    'productGrade' : '',                            # 产品等级
                    'price' : item[u'price_history'],               # 价格历史
                    'priceCurrency' : 'CNY',                           # 价格货币，命名规则使用iso-4217
                    'validDate' : '',                               # 有效日期
                    'productPlaceOfOrigin' : item['info'][u'产地'],  # 原产地
                    'maxPrice' : '',                                # 最高价
                    'seller' : '',                                  # 销售
                    'source' : '',                                  # 数据源url
                    'tags' : '',                                    # 标签   
                    'productionYear' : '',                          # 生产年限
                    'unitText' : item['info'][u'规格'],              # 单位，规格
                    'mainEntityOfPage' : '',                        # 
                    'sellerMarket' : '',                            # 报送单位(在中华粮网里出现，是各地市场)
                    'minPrice' : '',                                # 最低价
                    'productSpecification' : '',                    # 产品说明
                    'priceType' : '',                               # 价格类型
                    'description' : '',                             # 产品描述
            }

            return item_suit_schema

    def run(self):
        self.set_source_files_path()
        for file_path in self.source_files_path:
            self.parse_single_file(file_path)

# class hjson_extractor_for_cngarin(hjson_extractor):
#     def parse_single_item(self, item):
#         ......
    
m = hjson_extractor('ytyaocai')
m.run()
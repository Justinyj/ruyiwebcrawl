#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# cleaning codes for agricul and chemppi

from hprice_cleaning import HpriceCleansing
from to_es import sendto_es
from datetime import datetime

class Shengyishecleansing(HpriceCleansing):
    def parse_single_item(self, item):
        item_suit_schema = self.init_item_schema()
        item_suit_schema['productGrade'] = item[u'详细信息'][u'等级'] if u'等级' in item[u'详细信息'] else None
        item_suit_schema['price'] = ''.join([i for i in item[u'商品报价'] if i.isdigit() or i == '.'])                        # 价格历史
        item_suit_schema['priceCurrency'] = 'CNY'                        # 价格货币，命名规则使用iso-4217
        item_suit_schema['confidence'] = 0.7
        item_suit_schema['validDate'] = item[u'发布时间']                               # 爬取日期
        item_suit_schema['productPlaceOfOrigin'] = item[u'出产地']        # 原产地
        item_suit_schema['source'] = item[u'url']                        # 数据源url
        item_suit_schema['unitText'] = ''.join([i for i in item[u'商品报价'] if not i.isdigit() and not i == '.'])              # 单位，规格
        item_suit_schema['mainEntityOfPage_raw'] = item[u'name']                        # 
        item_suit_schema['sellerMarket'] = item[u'报价机构']                            # 报送单位(在中华粮网里出现，是各地市场)
        item_suit_schema['priceType'] = item[u'报价类型']                               # 价格类型
        self.clean_item_schema(item_suit_schema)
        item_suit_schema[u'id'] = item_suit_schema[u'name'] + '_' + item_suit_schema[u'validDate']
        self.clean_item_data(item_suit_schema)
        self.jsons.append(item_suit_schema)
        self.counter += 1
        if self.counter == 2000:
            sendto_es(self.jsons)
            self.counter = 0
            self.jsons = []

if __name__ == '__main__':
    s = Shengyishecleansing('agricul')
    c = Shengyishecleansing('chemppi')
    s.run()
    c.run()

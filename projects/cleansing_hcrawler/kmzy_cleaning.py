#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# cleansing codes for kmzy

from hprice_cleaning import HpriceCleansing
from datetime import datetime

class Kmzycleansing(HpriceCleansing):
    def parse_single_item(self, item):
        item_suit_schema = self.init_item_schema()
        item_suit_schema['productGrade'] = item[u'specs'].split('/')[0]                            # 产品等级
        item_suit_schema['priceCurrency'] = 'CNY'                        # 价格货币，命名规则使用iso-4217
        item_suit_schema['confidence'] = 0.7
        item_suit_schema['productPlaceOfOrigin'] = item[u'specs'].split('/')[1]        # 原产地
        item_suit_schema['source'] = item[u'source']                        # 数据源url
        item_suit_schema['unitText'] = None              # 单位，规格
        item_suit_schema['mainEntityOfPage_raw'] = item[u'name']     
        item_suit_schema['priceType']= None   
        item_suit_schema['sellerMarket']=None                # 


        self.clean_item_schema(item_suit_schema)
        item_suit_schema['name'] = item[u'name'] +'_' + item[u'specs'].split('/')[1] + '_' + item[u'specs'].split('/')[0]                 

        for mon, price in item['data']:
            result_item = item_suit_schema.copy()
            result_item['price'] = price
            result_item['validDate'] = mon
            result_item[u'id']  = result_item[u'name'] + '_' + result_item[u'validDate']
            self.clean_item_data(result_item)
            self.jsons.append(result_item)
            self.counter += 1
            if self.counter == 2000:
                sendto_es(self.jsons)
                self.counter = 0
                self.jsons = []

if __name__ == '__main__':
    k = Kmzycleansing('kmzy-20160808')
    k.run()
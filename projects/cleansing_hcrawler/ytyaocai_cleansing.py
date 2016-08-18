#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
from to_es import sendto_es
from hprice_cleaning import HpriceCleansing
from datetime import datetime

class YtyaocaiCleansing(HpriceCleansing):
    def parse_single_item(self, item):
            # 时间关系，这里暂时设成父类方法为分析药通网，未来可以调整优化
            # 药通网的price_history是一个字典，key为日期，value为价格
        item_suit_schema = self.init_item_schema()
        item_suit_schema['productPlaceOfOrigin'] = item[u'info'][u'产地']
        item_suit_schema['source']  = item[u'source']
        item_suit_schema['unitText'] = u'元/公斤'
        item_suit_schema['productSpecification'] = item[u'info'][u'规格'], 
        self.clean_item_schema(item_suit_schema)

        for k,v in item[u'price_history'].iteritems():
            result_item = item_suit_schema.copy()
            result_item['validDate'] = k   #日期
            result_item['price']     = v   #价格
            result_item['id']  = result_item['name'] + '_' + result_item['validDate']

            self.clean_item_data(result_item)
            self.jsons.append(result_item)
            self.counter += 1
            if self.counter >= 2000:
                sendto_es(self.jsons)
                self.counter = 0
                self.jsons = []

# class HpriceCleansingOfCngarin(HpriceCleansing):
#     #中华粮网每个json是一个市场，里面有若干种品种
#     def parse_single_item(self, item):
if __name__ == '__main__':
    m = YtyaocaiCleansing('ytyaocai-20160815')
    m.run()

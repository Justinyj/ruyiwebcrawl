#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# cleaning codes for agricul and chemppi

from hprice_cleaning import HpriceCleansing
from to_es import sendto_es
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
class CngrainCleansing(HpriceCleansing):
    def parse_single_item(self, item):

        for product in item['product_list']:
            item_suit_schema = self.init_item_schema()
            item_suit_schema['productGrade'] = product[u'level'] 
            item_suit_schema['priceCurrency'] = 'CNY'
            item_suit_schema['confidence'] = 0.7
            item_suit_schema['productPlaceOfOrigin'] = product['produce_area']       
            item_suit_schema['source'] = item[u'source']        
            item_suit_schema['productionYear'] = product[u'produce_year']                         
            item_suit_schema['unitText'] = u'元/吨'   
            item_suit_schema['mainEntityOfPage_raw'] = product[u'variety']  
            item_suit_schema['sellerMarket'] = item[u'market']  
            item_suit_schema['priceType'] = product[u'price_type']

            self.clean_item_schema(item_suit_schema)

            if not product[u'price_history']: #由于部分数据没有价格历史，因此先在上面将其赋值为空，再在后面for循环里覆盖
                result_item = item_suit_schema.copy()
                result_item['id']  = item_suit_schema['name'] + '_'
                self.clean_item_data(result_item)
                self.jsons.append(result_item)
                self.counter += 1
                return

            for k,v in product[u'price_history'].iteritems():
                result_item = item_suit_schema.copy()
                result_item[u'validDate'] = k   #日期
                result_item[u'price']     = v   #价格
                result_item[u'id']  = result_item[u'name'] + '_' + result_item[u'validDate']
                self.clean_item_data(result_item)
                self.jsons.append(result_item)
                self.counter += 1
                if self.counter >= 2000:
                    sendto_es(self.jsons)
                    self.counter = 0
                    self.jsons = []

if __name__ == '__main__':
    s = CngrainCleansing('cngrain-20160817')
    s.run()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# cleaning codes for agricul and chemppi

from hprice_cleaning import HpriceCleansing
from datetime import datetime
from to_es import sendto_es
import re
class CngrainCleansing(HpriceCleansing):
    def parse_single_item(self, item):

        for product in item['product_list']:
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
                    'sellerMarket' :            None,   # 报送单位(在中华粮网里出现，是各地市场)
                    'minPrice' :                None,   # 最低价
                    'productSpecification' :    None,   # 产品规格
                    'priceType' :               None,   # 价格类型
                    'description' :             None,   # 产品描述
                }
            item_suit_schema['createdTime'] = datetime.today().isoformat()
            item_suit_schema['productGrade'] = product[u'level'] 
            item_suit_schema['priceCurrency'] = 'CNY'                        # 价格货币，命名规则使用iso-4217
            item_suit_schema['createdTime'] = datetime.today().isoformat()
            item_suit_schema['confidence'] = 0.7
            item_suit_schema['productPlaceOfOrigin'] = product['produce_area']        # 原产地
            item_suit_schema['source'] = item[u'source']                        # 数据源url
            item_suit_schema['productionYear'] = product[u'produce_year']                          # 生产年限
            item_suit_schema['unitText'] = u'元/kg'              # 
            item_suit_schema['mainEntityOfPage'] = product[u'variety']                         # 
            item_suit_schema['sellerMarket'] = item[u'market']                            # 报送单位
            item_suit_schema['priceType'] = product[u'price_type']

            item_suit_schema['name'] = ('{}_{}_{}_{}').format(item_suit_schema['mainEntityOfPage'], item_suit_schema['priceType'], item_suit_schema['sellerMarket'], item_suit_schema['productGrade'])
            domin = re.findall('http://(.*?)/', item_suit_schema['source'])[0]
            self.myset.add( domin + ',' +item_suit_schema['name'])
            if not product[u'price_history']: #由于部分数据没有价格历史，因此先在上面将其赋值为空，再在后面for循环里覆盖
                result_item = item_suit_schema.copy()
                result_item['id']  = item_suit_schema['name'] + '_'
                self.jsons.append(result_item)
                self.counter += 1
                return

            for k,v in product[u'price_history'].iteritems():
                result_item = item_suit_schema.copy()
                result_item[u'validDate'] = k   #日期
                result_item[u'price']     = v   #价格
                result_item[u'id']  = result_item[u'name'] + '_' + result_item[u'validDate']
                self.jsons.append(result_item)
                self.counter += 1
                if self.counter >= 2000:
                    sendto_es(self.jsons)
                    self.counter = 0
                    self.jsons = []

if __name__ == '__main__':
    s = CngrainCleansing('cngrain-20160817')
    s.run()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# cleaning codes for agricul and chemppi

from hprice_cleaning import HpriceCleansing
from datetime import datetime
from to_es import sendto_es

class Syscleansing(HpriceCleansing):
    def parse_single_item(self, item):

        for product in item['product_list']:
            item_suit_schema = {
                'name' : product[u'variety'] + '_' + product[u'price_type'] + '_' + item[u'market'] + '_' + product[u'level'],                         # 品种
                'productGrade' : product[u'level'] ,
                'price' : '',
                'priceCurrency' : 'CNY',                        # 价格货币，命名规则使用iso-4217
                'createdTime' : datetime.today().isoformat(),
                'confidence' : 0.7,
                'validDate' : '',
                'productPlaceOfOrigin' : product['produce_area'],        # 原产地
                'maxPrice' : '',                                # 最高价
                'seller' : '',                                  # 销售
                'source' : item[u'source'],                        # 数据源url
                'tags' : '',                                    # 标签   
                'productionYear' : product[u'produce_year'],                          # 生产年限
                'unitText' : u'元/kg',              # 
                'mainEntityOfPage' : product[u'variety'] ,                        # 
                'sellerMarket' : item[u'market'],                            # 报送单位
                'minPrice' : '',                                # 最低价
                'productSpecification' : '',                    # 产品规格
                'priceType' : product[u'price_type'],                               # 价格类型
                'description' : '',                             # 产品描述
            }
            if not product[u'price_history']: #由于部分数据没有价格历史，因此先在上面将其赋值为空，再在后面for循环里覆盖
                result_item = item_suit_schema.copy()
                result_item['id']  = item_suit_schema['name']
                self.jsons.append(result_item)
                self.counter += 1
                return

            for k,v in product[u'price_history'].iteritems():
                result_item = item_suit_schema.copy()
                result_item['validDate'] = k   #日期
                result_item['price']     = v   #价格
                result_item['id']  = result_item['name'] + '_' + result_item['validDate']
                self.jsons.append(result_item)
                self.counter += 1
                if self.counter >= 2000:
                    sendto_es(self.jsons)
                    self.counter = 0
                    self.jsons = []

if __name__ == '__main__':
    s = Syscleansing('cngrain-20160817')
    s.run()

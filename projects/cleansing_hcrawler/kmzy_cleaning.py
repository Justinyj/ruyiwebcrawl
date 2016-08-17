#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>
# cleansing codes for kmzy

from hprice_cleaning import HpriceCleansing
from datetime import datetime

class Kmzycleansing(HpriceCleansing):
    def parse_single_item(self, item):
        for mon, price in item['data']:
            item_suit_schema = {
                        'id' : item[u'name'] + '_' + item[u'specs'].split('/')[1] + '_' + item[u'specs'].split('/')[0] + '_' + mon,
                        'name' : item[u'name'] + '_' + item[u'specs'].split('/')[1] + '_' + item[u'specs'].split('/')[0],                         # 品种
                        'productGrade' : item[u'specs'].split('/')[0],                            # 产品等级
                        'price' : price,                        # 价格历史
                        'priceCurrency' : 'CNY',                        # 价格货币，命名规则使用iso-4217
                        'validDate' : mon,                               # 爬取日期
                        'createdTime' : datetime.today().isoformat(),
                        'confidence' : 0.7,
                        'productPlaceOfOrigin' : item[u'specs'].split('/')[1],        # 原产地
                        'maxPrice' : None,                                # 最高价
                        'seller' : None,                                  # 销售
                        'source' : item[u'source'],                        # 数据源url
                        'tags' : None,                                    # 标签   
                        'productionYear' : None,                          # 生产年限
                        'unitText' : None,              # 单位，规格
                        'mainEntityOfPage' : item[u'name'],                        # 
                        'sellerMarket' : None,                            # 报送单位(在中华粮网里出现，是各地市场)
                        'minPrice' : None,                                # 最低价
                        'productSpecification' : None,                    # 产品说明
                        'priceType' : None,                               # 价格类型
                        'description' : None,                             # 产品描述
                }
            self.jsons.append(item_suit_schema)
            self.counter += 1
            if self.counter == 2000:
                sendto_es(self.jsons)
                self.counter = 0
                self.jsons = []

if __name__ == '__main__':
    k = Kmzycleansing('kmzy-20160808')
    k.run()
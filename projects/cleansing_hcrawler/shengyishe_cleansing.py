#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yingqi Wang <yingqi.wang93 (at) gmail.com>

from hprice_cleaning import HpriceCleansing

class Syscleansing(HpriceCleansing):
    def parse_single_item(self, item):
        item_suit_schema = {
                    'name' : item[u'报价类型'] + '-' + item[u'报价机构'],                         # 品种
                    'productGrade' : item[u'详细信息'][u'等级'],                            # 产品等级
                    'price' : ''.join([i for i in item[u'商品报价'] if i.isdigit()]),                        # 价格历史
                    'priceCurrency' : 'CNY',                        # 价格货币，命名规则使用iso-4217
                    'validDate' : item[u'发布时间'],                               # 爬取日期
                    'productPlaceOfOrigin' : item[u'出产地'],        # 原产地
                    'maxPrice' : '',                                # 最高价
                    'seller' : '',                                  # 销售
                    'source' : item[u'url'],                        # 数据源url
                    'tags' : '',                                    # 标签   
                    'productionYear' : '',                          # 生产年限
                    'unitText' : ''.join([i for i in item[u'商品报价'] if not i.isdigit()]),              # 单位，规格
                    'mainEntityOfPage' : item[u'name'],                        # 
                    'sellerMarket' : item[u'报价机构'],                            # 报送单位(在中华粮网里出现，是各地市场)
                    'minPrice' : '',                                # 最低价
                    'productSpecification' : '',                    # 产品说明
                    'priceType' : item[u'报价类型'],                               # 价格类型
                    'description' : '',                             # 产品描述
            }
        self.jsons.append(item_suit_schema)
        self.counter += 1
        if self.counter == 2000:
            sendto_es(self.jsons)
            self.counter = 0
            self.jsons = []


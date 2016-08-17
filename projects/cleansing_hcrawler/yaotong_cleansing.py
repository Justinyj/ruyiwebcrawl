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

            for k,v in item[u'price_history'].iteritems():
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
                item_suit_schema['priceCurrency'] = 'CNY'
                item_suit_schema['confidence']    = 0.7
                item_suit_schema['productPlaceOfOrigin'] = item[u'info'][u'产地']
                item_suit_schema['source']  = item[u'source']
                item_suit_schema['unitText'] = u'元/公斤'
                item_suit_schema['productSpecification'] = item[u'info'][u'规格'], 
                item_suit_schema['name'] = ('{}_{}_{}_{}').format(item_suit_schema['mainEntityOfPage'], item_suit_schema['priceType'], item_suit_schema['sellerMarket'], item_suit_schema['productGrade'])

                item_suit_schema['validDate'] = k   #日期
                item_suit_schema['price']     = v   #价格
                item_suit_schema['id']  = item_suit_schema['name'] + '_' + item_suit_schema['validDate']
                self.jsons.append(item_suit_schema)
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

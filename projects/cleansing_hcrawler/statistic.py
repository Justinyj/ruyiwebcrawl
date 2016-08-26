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
        item_suit_schema = {}
        item_suit_schema['mainEntityOfPage_raw'] = item['name']
        item_suit_schema['productPlaceOfOrigin'] = item['productPlaceOfOrigin']
        item_suit_schema['sellerMarket'] = item['sellerMarket']
        item_suit_schema['productGrade'] = item['productGrade']
        item_suit_schema['source'] = item['detail_url']
        self.clean_item_schema(item_suit_schema)


if __name__ == '__main__':
    s = CngrainCleansing('yaotongnew-20160823')
    s.run()
    
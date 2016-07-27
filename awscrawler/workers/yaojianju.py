#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

from __future__ import print_function, division

import json
import urllib
import re
import urlparse
import lxml.html
from datetime import datetime

from downloader.downloader_wrapper import Downloader
from downloader.downloader_wrapper import DownloadWrapper

from crawlerlog.cachelog import get_logger
from settings import REGION_NAME


def process(url, batch_id, parameter, manager, *args, **kwargs):
    home_page = 'http://app1.sfda.gov.cn/datasearch/face3/base.jsp?tableId=25&tableName=TABLE25&title=%B9%FA%B2%FA%D2%A9%C6%B7&bcId=124356560303886909015737447882'
    if not hasattr(process, '_downloader'):
        domain_name =  Downloader.url2domain(url)
        headers = {'Host': domain_name}
        setattr(process, '_downloader', DownloadWrapper('http://192.168.1.179:8000', headers, REGION_NAME))

    if not hasattr(process,'_reg'):
        setattr(process, '_reg', {
            'detail': re.compile('http://app1.sfda.gov.cn/datasearch/face3/content.jsp\?tableId=25&tableName=TABLE25&tableView=%B9%FA%B2%FA%D2%A9%C6%B7&Id=(\d+)'),
        })

    method, gap, js, timeout, data = parameter.split(':')
    gap = int(gap)
    timeout= int(timeout)

    data = {
        'tableId' : '25',
        'State' : '1',
        'bcId' : '124356560303886909015737447882',
        'State' : '1',
        'curstart' : 1,  #here!
        'State' : '1',
        'tableName' : 'TABLE25',
        'State' : '1',
        'viewtitleName' : 'COLUMN167',
        'State' : '1',
        'viewsubTitleName' : 'COLUMN166,COLUMN170,COLUMN821',
        'State' : '1',
        'tableView' : '%E5%9B%BD%E4%BA%A7%E8%8D%AF%E5%93%81',
        'State' : '1',
    }

    if url == home_page:
        print ('homte')
        page = 1
        while 1 :
            data['curstart'] = page
            content = process._downloader.downloader_wrapper('http://app1.sfda.gov.cn/datasearch/face3/search.jsp',
                batch_id,
                gap,
                method = 'post',
                timeout = timeout,
                refresh = True,
                data = data
            )
            if page == 3:
                return
            ids = re.findall(u'国产药品&Id=(\d+)', content)
            if not ids:
                break
            url_pattern = 'http://app1.sfda.gov.cn/datasearch/face3/content.jsp?tableId=25&tableName=TABLE25&tableView=%B9%FA%B2%FA%D2%A9%C6%B7&Id={}'
            urls = []
            for drug_id in ids:
                url = url_pattern.format(drug_id)
                urls.append(url)
            manager.put_urls_enqueue(batch_id, urls)
            page += 1

    elif process._reg['detail'].match(url):
        content = process._downloader.downloader_wrapper(
            url,
            batch_id,
            gap,
            timeout=timeout,
            )
        if content == '':
            return False
        dom = lxml.html.fromstring(content)
        table = dom.xpath('//tr')

        item = {
            'license_number':       table[1].xpath('./td')[1].xpath('./text()'),  #[u'批准文号'],
            'product_name_chs':     table[2].xpath('./td')[1].xpath('./text()'),  #[u'产品名称'],
            'product_name_eng':     table[3].xpath('./td')[1].xpath('./text()'),  #[u'英文名称'],
            'commodity_name_chs':   table[4].xpath('./td')[1].xpath('./text()'),  #[u'商品名'],
            'drug_form':            table[5].xpath('./td')[1].xpath('./text()'),  #[u'剂型'],
            'specification':        table[6].xpath('./td')[1].xpath('./text()'),  #[u'规格'],
            'manufacturer_chs':     table[7].xpath('./td')[1].xpath('./text()'),  #[u'生产单位'],
            'manuf_address_chs':    table[8].xpath('./td')[1].xpath('./text()'),  #[u'生产地址'],
            'category':             table[9].xpath('./td')[1].xpath('./text()'),  #[u'产品类别'],
            'license_data':         table[11].xpath('./td')[1].xpath('./text()'), #[u'批准日期'],
            'standard_code':        table[12].xpath('./td')[1].xpath('./text()'), #[u'药品本位码'],
            'standard_code_remark': table[13].xpath('./td')[1].xpath('./text()'), #[u'药品本位码备注'],
        }
        for k,v in item.iteritems():
            if len(v) > 0:
                item[k] = v[0]
            else :
                item[k] = None
        with open('drug.txt', 'a+') as f:
            line = json.dumps(item, ensure_ascii = False)
            f.write(line.encode('utf-8'))
            f.write('\n')
    return True



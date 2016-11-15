#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

import json
import os
import collections
import datetime
from collections import defaultdict
from yaojianjugmpgsp_loader import YaojianjugmpgspLoader
import lxml.html

excel_path = '/Users/johnson/yaojianjugmpgsp_excel'
output_path = '/Users/johnson/yaojianjugmpgsp_jsn'
def getExcelCellValue(workbook, sheet, row, col):
    '''http://stackoverflow.com/questions/17827471/python-xlrd-discerning-dates-from-floats'''
    import xlrd
    cell_value = sheet.cell_value(row,col)
    cell_type = sheet.cell_type(row,col)
    if cell_type == xlrd.XL_CELL_DATE:
        dt_tuple = xlrd.xldate_as_tuple(cell_value, workbook.datemode)
        #print dt_tuple
        cell_value = "%04d-%02d-%02d" % ( dt_tuple[0], dt_tuple[1], dt_tuple[2])
    if type(cell_value) in [unicode, basestring]:
        cell_value = cell_value.strip()
    return cell_value

def readExcel(headers, filename, start_row=0, non_empty_col=-1, file_contents=None):
    # 此版本为了适配药监局excel格式，经些许微调     ————zyx
    # http://www.lexicon.net/sjmachin/xlrd.html
    import xlrd
    counter = collections.Counter()
    if file_contents:
        workbook = xlrd.open_workbook(file_contents=file_contents)
    else:
        workbook = xlrd.open_workbook(filename)

    ret = defaultdict(list)
    for name in workbook.sheet_names():
        sh = workbook.sheet_by_name(name)
        for row in range(start_row, sh.nrows):
            item={}
            rowdata = sh.row(row)
            if len(rowdata)< len(headers):
                print( "skip %s ", json.dumps(rowdata, ensure_ascii=False))
                continue

            for col in range(len(rowdata)):
                item[col]= getExcelCellValue(workbook, sh, row, col)

            if non_empty_col>=0 and not item[headers[non_empty_col]]:
                #print "skip empty cell"
                continue

            ret[name].append(item)


    return ret

def read_from_excel(excel_file):
    outer_header = [u'title', u'published_time', u'article_content', u'source', u'附件地址']
    raw_result = readExcel([],excel_file)
    for sheet, rows in raw_result.iteritems():
        header_row = rows[0]
        jsn = {
            'table_list':[],
        }
        headers = []
        for num, header in header_row.iteritems():
            headers.append(header)
        for row in rows[1:]:
            table = {
                'access_time': datetime.datetime.utcnow().isoformat(),
            }
            for num, content in row.iteritems():
                if not content:
                    continue
                elif headers[num] in outer_header:
                    jsn[headers[num]] = content
                else:
                    table[headers[num]] = content
            jsn['table_list'].append(table)
    return jsn





def main(excel_path):
    files = os.listdir(excel_path)

    for file in files:
        print file
        jsn = read_from_excel(os.path.join(excel_path, file))
        with open(os.path.join(output_path, file.replace('.xlsx', '')), 'w') as f:
            f.write(json.dumps(jsn, ensure_ascii=False))

def main2(jsn_path):
    files = os.listdir(jsn_path)
    obj = YaojianjugmpgspLoader()
    obj.read_from_mapping()
    obj.tag_counter = {}
    cc = 0
    for file in files:
        with open(os.path.join(jsn_path, file), 'r') as f:
            jsn = json.load(f)
            obj.parse(jsn)
    print json.dumps(obj.tag_counter, ensure_ascii=False)

if __name__ ==  '__main__':
    # main(excel_path)
    main2(output_path)

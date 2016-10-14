# encoding=utf-8
'''
change log
2016-05-24    created
2016-08-15    readExcel2
2016-08-17    readExcel2 change output format {'data':...,'fields':....}
'''

import glob
import os
import sys
import json
import collections
from collections import defaultdict
import codecs
import re
import hashlib

def genEsId(text):
    #assert question as utf8
    text =text.encode('utf-8')
    return hashlib.md5(text).hexdigest()

def writeExcel(items, keys, filename, page_size=60000, debug=False):
    import xlwt
    wb = xlwt.Workbook()
    rowindex =0
    sheetindex=0
    for item in items:
        if rowindex % page_size ==0:
            sheetname = "%02d" % sheetindex
            ws = wb.add_sheet(sheetname)
            rowindex = 0
            sheetindex +=1

            colindex =0
            for key in keys:
                ws.write(rowindex, colindex, key)
                colindex+=1
            rowindex +=1

        colindex =0
        for key in keys:
            v = item.get(key,"")
            if type(v) == list:
                v = ','.join(v)
            if type(v) == set:
                v = ','.join(v)
            ws.write(rowindex, colindex, v)
            colindex+=1
        rowindex +=1

    if debug:
        print filename
    wb.save(filename)


def readExcel(headers, filename, start_row=0, non_empty_col=-1, file_contents=None):
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
                print "skip",rowdata
                continue

            for col in range(len(headers)):
                value = sh.cell(row,col).value
                if type(value) in [unicode, basestring]:
                    value = value.strip()
                item[headers[col]]= value

            if non_empty_col>=0 and not item[headers[non_empty_col]]:
                #print "skip empty cell"
                continue

            ret[name].append(item)
        print "loaded",filename, len(ret[name])
    return ret

def readExcel2(filename, non_empty_col=0, file_contents=None):
    # http://www.lexicon.net/sjmachin/xlrd.html
    import xlrd
    counter = collections.Counter()
    if file_contents:
        workbook = xlrd.open_workbook(file_contents=file_contents)
    else:
        workbook = xlrd.open_workbook(filename)

    start_row = 0
    ret = defaultdict(list)
    fields = {}
    for name in workbook.sheet_names():
        sh = workbook.sheet_by_name(name)
        headers = []
        for col in range(len(sh.row(start_row))):
            headers.append(sh.cell(start_row,col).value)
        print headers
        fields[name]= headers

        for row in range(start_row+1, sh.nrows):
            item={}
            rowdata = sh.row(row)
            if len(rowdata)< len(headers):
                print "WARNING: skip mismatched row",rowdata
                continue

            for col in range(len(headers)):
                value = sh.cell(row,col).value
                if type(value) in [unicode, basestring]:
                    value = value.strip()
                item[headers[col]]= value

            if non_empty_col>=0 and not item[headers[non_empty_col]]:
                #print "skip empty cell"
                continue

            ret[name].append(item)
        print "loaded",filename, len(ret[name])
    return {'data':ret,'fields':fields}


def file2list(filename, encoding='utf-8'):
    ret = list()
    visited = set()
    with codecs.open(filename,  encoding=encoding) as f:
        for line in f:
            line = line.strip()
            #skip comment line
            if line.startswith('#'):
                continue

            if line and line not in visited:
                ret.append(line)
                visited.add(line)
    return ret

def file2set(filename, encoding='utf-8'):
    ret = set()
    with codecs.open(filename,  encoding=encoding) as f:
        for line in f:
            line = line.strip()
            #skip comment line
            if line.startswith('#'):
                continue

            if line and line not in ret:
                ret.add(line)
    return ret

def lines2file(lines, filename, encoding='utf-8'):
    with codecs.open(filename, "w", encoding=encoding) as f:
        for line in lines:
            f.write(line)
            f.write("\n")

def json2file(data, filename,encoding ='utf-8'):
    with codecs.open(filename, "w", encoding=encoding) as f:
        json.dump(data, f, ensure_ascii=False, indent=4, sort_keys=True)

def items2file(items, filename,encoding ='utf-8', modifier='w'):
    with codecs.open(filename, modifier, encoding=encoding) as f:
        for item in items:
            f.write("{}\n".format(json.dumps(item, ensure_ascii=False)))


def read_file(fname, jsn=False):
    """
    :param ret: content, json, line, line_json
    """
    with codecs.open(fname, 'r') as fd:
        if jsn:
            return json.load(fd)
        else:
            return fd.read()

def read_file_iter(fname, jsn=False):
    with codecs.open(fname, 'r') as fd:
        if jsn:
            for line in fd:
                line = line.strip()
                if line:
                    yield json.loads(line)
        else:
            for line in fd:
                line = line.strip()
                if line:
                    yield line


def write_file(fname, lines, jsn=False):
    with codecs.open(fname, 'w', encoding='utf-8') as fd:
        if jsn:
            json.dump(lines, fd, ensure_ascii=False, indent=4)
        else:
            fd.write('\n'.join(lines))

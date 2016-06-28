#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import codecs
import lxml.html
import json
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


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
                yield json.loads(line.strip())
        else:
            for line in fd:
                yield line.strip()


def write_file(fname, lines, jsn=False):
    with codecs.open(fname, 'w', encoding='utf-8') as fd:
        if jsn:
            json.dump(lines, fd, ensure_ascii=False, indent=4)
        else:
            fd.write('\n'.join(lines))



def zgdbk_parse_entity(entity):
    if entity.startswith('<font'):
        return entity[entity.find('red>')+4:].replace('</font>', '')
    if entity.startswith('\xee'): # human unreadable string
        return
    return entity

def zgdbk_extract_entity(infilename):
    entities = set()
    re_entity = re.compile('<span id="span2" class="STYLE2">(.+)</span')

    for line in read_file_iter(infilename):
        m = re_entity.match(line)
        if m:
            entity = zgdbk_parse_entity( m.group(1) )
            if entity:
                entities.add(entity)

    write_file('entities/zgdbk_entities.txt', entities)
    print('zgdbk entities length: ', len(entities))
    return entities


def bdbk_extract_entity(ifilename):
    entities = set()
    last_line = '</>'

    for line in read_file_iter(ifilename):
        if last_line == '</>':
            entities.add(line)
        elif line.startswith('@@@LINK='):
            entities.add(line[8:])
        last_line = line

    write_file('entities/{}_entities.txt'.format(ifilename), entities)
    print('bdbk entities length: ', len(entities))
    return entities


def wiki_extract_entity():
    entities = set()
    disambiguation = re.compile('(.*)_\([^\)]+\)')

    for jsn in read_file_iter('wikidata_zh_simplified.json', jsn=True):
        m = disambiguation.match(jsn['chinese_label'])
        item = m.group(1) if m else jsn['chinese_label']
        entities.add(item)
        if 'chinese_aliases' in js:
            entities.update(js['chinese_aliases'])

    for jsn in read_file_iter('merge_step_5_simplified.json', jsn=True):
        key = jsn.keys()[0]
        entities.add( key[key.rfind('/') + 1:-1] )

    write_file('entities/wiki_entities.txt', entities)
    print('wiki entities length: ', len(entities))
    return entities


def wiki_title_entity(fname):
    entities = set()
    disambiguation = re.compile('(.*)_\([^\)]+\)')

    for line in read_file_iter(fname):
        m = disambiguation.match(line.strip())
        item = m.group(1) if m else line.strip()
        if not item.startswith('\xee'): # human unreadable string
            entities.add(item)

    write_file('{}_title', entities)
    print('wiki title entities length: ', len(entities))
    return entities



if __name__ == '__main__':
    entities = set()

    entities.update( zgdbk_extract_entity('zgdbk.txt') )
    entities.update( bdbk_extract_entity('vbk2012.txt') )
    entities.update( bdbk_extract_entity('vbk2012_ext.txt') )
    entities.update( wiki_extract_entity() )
    entities.update( wiki_title_entity('zhwiki-20160601-all-titles-in-ns0.txt') )
    entities.update( wiki_title_entity('zhwiki-20160601-all-titles-in-ns1.txt') )

    write_file('entityes_0628_raw.txt', entities)


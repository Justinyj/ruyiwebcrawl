#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
#
# lower of entities should be do in filter, when entities used for search.
# if use the original dataset, lower should not be used when import to es.

from __future__ import print_function, division

import codecs
import json
import re
import string
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

from hzlib.libfile import read_file_iter, write_file
from filter_lib import regdisambiguation, regdropbrackets, regrmlabel


def zgdbk_parse_entity(entity):
    if entity.startswith('<font'):
        return entity[entity.find('red>')+4:].replace('</font>', '')
    if entity.startswith('\xee'): # human unreadable string
        return
    return entity

def zgdbk_extract_entity(infilename, persistent=False):
    entities = set()
    re_entity = re.compile('<span id="span2" class="STYLE2">(.+)</span')

    for line in read_file_iter(infilename):
        m = re_entity.match(line)
        if m:
            entity = regrmlabel( m.group(1) )
            entity = zgdbk_parse_entity(entity)
            if entity:
                entities.add(entity.strip())

    print('zgdbk entities length: ', len(entities))
    if persistent:
        write_file('entities/zgdbk_entities.txt', entities)
    return entities


def bdbk_extract_entity(ifilename, persistent=False):
    entities = set()
    last_line = '</>'

    for line in read_file_iter(ifilename):
        if last_line == '</>':
            entities.add(line)
        elif line.startswith('@@@LINK='):
            entities.add(line[8:])
        last_line = line

    print('bdbk entities length: ', len(entities))
    if persistent:
        write_file('entities/{}_entities.txt'.format(ifilename), entities)
    return entities


def wiki_extract_entity(fname, persistent=False):
    entities = set()

    for jsn in read_file_iter(fname, jsn=True):
        m = regdisambiguation.match(jsn[u'chinese_label'])
        item = m.group(1) if m else jsn[u'chinese_label']
        entities.add(item.encode('utf-8').strip())
        if u'chinese_aliases' in jsn:
            entities.update(map(string.strip, map(lambda x: x.encode('utf-8'), jsn[u'chinese_aliases'])))

    print('wiki entities length: ', len(entities))
    if persistent:
        write_file('entities/wiki_entities.txt', entities)
    return entities


def dbpedia_extract_entity(fname, persistent=False):
    entities = set()

    for jsn in read_file_iter(fname, jsn=True):
        key, value = jsn.items()[0]
        key = value[u'resource_label'].strip()

        m = regdisambiguation.match(key)
        entity = m.group(1) if m else key
        entities.add(entity.encode('utf-8'))

    print('dbpedia entities length: ', len(entities))
    if persistent:
        write_file('entities/dbpedia_entities.txt', entities)
    return entities


def wiki_title_entity(fname, persistent=False):
    entities = set()

    for line in read_file_iter(fname):
        m = regdisambiguation.match(line.strip().decode('utf-8'))
        item = m.group(1).encode('utf-8') if m else line.strip()
        if not item.startswith('\xee'): # human unreadable string
            entities.add(item.strip())

    write_file('entities/{}_title'.format(fname), entities)
    if persistent:
        print('wiki title entities length: ', len(entities))
    return entities


def comic_song_extract_entity(fname, persistent=False):
    entities = set()

    for line in read_file_iter(fname):
        m = regdropbrackets.match(line.decode('utf-8'))
        entity = m.group(1).encode('utf-8') if m else line
        entities.add(entity)

    print('comic song entities length: ', len(entities))
    if persistent:
        write_file('entities/comic_song_entities.txt', entities)
    return entities


if __name__ == '__main__':
    entities = set()

    entities.update( zgdbk_extract_entity('zgdbk.txt', True) )
    entities.update( bdbk_extract_entity('vbk2012.txt', True) )
    entities.update( bdbk_extract_entity('vbk2012_ext.txt', True) )
    entities.update( wiki_extract_entity('wikidata_zh_simplified.json', True) )
    entities.update( dbpedia_extract_entity('merge_step_5_simplified.json', True) )
    entities.update( wiki_title_entity('zhwiki-20160601-all-titles-in-ns2.txt', True) )
    entities.update( comic_song_extract_entity('ertong.txt', True) )

    write_file('entities/entities_0630_raw.txt', entities)


#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
#
# zgdbk entities length:  59155
# comic song entities length:  3768
# zgdbk and comic length 62923
# dbpedia entities length:  731297
# wiki entities length:  1893688
# bdbk entities length:  2258551
# intersection length 193861

from __future__ import print_function, division

from hzlib.libfile import write_file
from load_entities import (zgdbk_extract_entity, comic_song_extract_entity,
        bdbk_extract_entity, wiki_extract_entity, dbpedia_extract_entity)

def run():
    entities = []

    entities.extend(list( zgdbk_extract_entity('zgdbk.txt') ))
    entities.extend(list( comic_song_extract_entity('ertong.txt') ))
    print('zgdbk and comic length', len(entities))

    dbpedia, wikidata, bdbk = load_db_data_bd()
    inter3, tidy_inter, db_wiki_each = intersection_of3(dbpedia, wikidata, bdbk)
    print('intersection length', len(inter3))
    print('dbpedia, wikidata unique intersection length', len(tidy_inter))

    entities.extend(list( db_wiki_each ))
    return entities

def load_db_data_bd():
    if not hasattr(load_db_data_bd, '_cache'):
        dbpedia = dbpedia_extract_entity('merge_step_5_simplified.json')
        wikidata = wiki_extract_entity('wikidata_zh_simplified.json')
        bdbk = bdbk_extract_entity('vbk2012.txt')
        setattr(load_db_data_bd, '_cache', (dbpedia, wikidata, bdbk))
    return load_db_data_bd._cache


def intersection_of3(dbpedia, wikidata, bdbk):
    if not hasattr(intersection_of3, '_cache'):
        inter_temp = dbpedia.intersection(wikidata)
        inter3 = inter_temp.intersection(bdbk)
        setattr(intersection_of3, '_cache', (inter3, inter_temp - inter3, inter_temp))
    return intersection_of3._cache


def get_dbpedia_wikidata():
    dbpedia, wikidata, bdbk = load_db_data_bd()
    _, _, db_wiki_each = intersection_of3(dbpedia, wikidata, bdbk)
    return list(dbpedia - db_wiki_each) + list(wikidata - db_wiki_each)


def get_bdbk():
    dbpedia, wikidata, bdbk = load_db_data_bd()
    return list( bdbk.difference(dbpedia).difference(wikidata) )



if __name__ == '__main__':
    first = run()
    write_file('entities/first_order_entities.txt', first)
    
    write_file('entities/second_order_entities.txt', get_dbpedia_wikidata())
    write_file('entities/third_order_entities.txt', get_bdbk())

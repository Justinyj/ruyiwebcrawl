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
    inter, tidy_inter = intersection_of3(dbpedia, wikidata, bdbk)
    print('intersection length', len(inter))

    entities.extend(list( inter ))
    return entities

def load_db_data_bd():
    dbpedia = dbpedia_extract_entity('merge_step_5_simplified.json')
    wikidata = wiki_extract_entity('wikidata_zh_simplified.json')
    bdbk = bdbk_extract_entity('vbk2012.txt')
    return dbpedia, wikidata, bdbk


def intersection_of3(dbpedia, wikidata, bdbk):
    inter_temp = dbpedia.intersection(wikidata)
    inter = inter_temp.intersection(bdbk)
    return inter, inter_temp - inter


def db_data_unique():
    dbpedia, wikidata, bdbk = load_db_data_bd()
    inter, tidy_inter = intersection_of3(dbpedia, wikidata, bdbk)
    print('dbpedia, wikidata unique intersection length', len(tidy_inter))
    return list(tidy_inter)


def sort_wiki():
    pass

def sort_dbpedia():
    pass

def sort_bdbk():
    pass

if __name__ == '__main__':
    write_file('entities/first_order_entities.txt', run())
    write_file('entities/second_order_entities.txt', db_data_unique())

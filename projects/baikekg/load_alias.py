#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import re
import os

from hzlib.libfile import read_file, read_file_iter, write_file
from filter_lib import regchinese, regdropbrackets

DIR = '/Users/bishop/百度云同步盘/'


def extract_bdbk_with_alias(ifilename):
    with open('{}_entities.txt'.format(ifilename), 'w') as wfd, codecs.open(ifilename) as rfd:
        last_line = '</>'

        for i, line in enumerate(rfd):
            line = line.strip()
            if last_line == '</>':
                if i == 0:
                    wfd.write(line)
                else:
                    wfd.write('\n' + line)
            elif line.startswith('@@@LINK='):
                wfd.write('\t' + line[8:])
            last_line = line

    entity_alias = {}
    with open('{}_entities.txt'.format(ifilename)) as fd:
        for line in fd:
            if '\t' in line:
                entity_alias.update( dict([line.strip().split('\t')]) )

    write_file('bdbk_entity_alias.json', entity_alias, jsn=True)


def load_bdbk_alias(dirname, fname):
    name = os.path.join(dirname, fname)
    return read_file(name, jsn=True)


def load_zhwiki_alias(dirname, fname):
    zhwiki_entity_alias = {}

    name = os.path.join(dirname, fname)
    for js in read_file_iter(name, jsn=True):
        if u'chinese_aliases' in js:
            zhwiki_entity_alias[js[u'chinese_label']] = js[u'chinese_aliases']

    return zhwiki_entity_alias

def load_merge_step5_wiki_simplified(dirname, fname):
    merge_step5_wiki_simplified = {}

    name = os.path.join(dirname, fname)
    for js in read_file_iter(name, jsn=True):
        for key, value in js.iteritems():
            entity = value[u'resource_label']
            if u'resource_alias' in value:
                merge_step5_wiki_simplified[entity] = value[u'resource_alias']
                m = regdropbrackets.match(entity)
                if m:
                    merge_step5_wiki_simplified[m.group(1)] = value[u'resource_alias']

    return merge_step5_wiki_simplified


def load_fudankg_alias(dirname):
    fudan_entity_alias = {}

    for f in os.listdir(dirname):
        jsn = read_file(os.path.join(dirname, f), jsn=True)
        for entity, avps in js.items():
            for a, v in avps[u'av pair']:
                if a == u'别名':
                    fudan_entity_alias[entity] = v
#    print(json.dumps(fudan_entity_alias, ensure_ascii=False, indent=4))
    return fudan_entity_alias


def get_all_aliases(entity):
    """
    :param entity: type(entity) is unicode
    """
    if not hasattr(get_all_aliases, '_aliases'):
        dirname = os.path.join(DIR, 'fudankg-json')
        _aliases = {
            'fudan': load_fudankg_alias(dirname),
            'bdbk': load_bdbk_alias(DIR, 'bdbk_entity_alias.json'),
            'zhwiki': load_zhwiki_alias(DIR, 'wikidata_zh_simplified.json'),
            'merge': load_merge_step5_wiki_simplified(DIR, 'merge_step_5_simplified.json'),
        }
        setattr(get_all_aliases, '_aliases', _aliases)

    alias_fd = get_all_aliases._aliases['fudan'].get(entity, None)
    alias_bdbk = get_all_aliases._aliases['bdbk'].get(entity, None)
    alias_zhwiki = get_all_aliases._aliases['zhwiki'].get(entity, None)
    alias_merge = get_all_aliases._aliases['merge'].get(entity, None)

    aliases = set()
    if alias_fd:
        aliases.update(map(lambda x: x.encode('utf-8'), alias_fd.split(u',')))
    if alias_bdbk:
        aliases.update(map(lambda x: x.encode('utf-8'), alias_bdbk.split(u',')))
    if alias_zhwiki:
        aliases.update([j.encode('utf-8') for i in alias_zhwiki for j in i.split(u',')])
    if alias_merge:
        aliases.update([j.encode('utf-8') for i in alias_merge for j in i.split(u',')])
    if entity.endswith(u'山脉'):
        aliases.add(entity.rstrip(u'脉').encode('utf-8'))

    removed = []
    for i in aliases:
        j = i.decode('utf-8')
        if len(j) == 1:
            removed.append(i)
        else:
            if regchinese.match(j) is None:
                removed.append(i)
    for i in removed:
        aliases.remove(i)
    return aliases


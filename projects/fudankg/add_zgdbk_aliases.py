#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import codecs
import json
import re
import os
import itertools
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

DIR = '/Users/bishop/百度云同步盘/'

def load_fudankg_alias(dirname):
    fudan_entity_alias = {}

    for f in os.listdir(dirname):
        with open(os.path.join(dirname, f)) as fd:
            for entity, avps in json.load(fd).items():
                for a, v in avps:
                    if a == u'别名':
                        fudan_entity_alias[entity] = v
#    print(json.dumps(fudan_entity_alias, ensure_ascii=False, indent=4))
    return fudan_entity_alias


def load_bdbk_alias(dirname, fname):
    name = os.path.join(dirname, fname)
    with open(name) as fd:
        return json.load(fd)


def load_zhwiki_alias(dirname, fname):
    zhwiki_entity_alias = {}

    name = os.path.join(dirname, fname)
    with open(name) as fd:
        for line in fd:
            js = json.loads(line.strip())
            if u'chinese_aliases' in js:
                zhwiki_entity_alias[js[u'chinese_label']] = js[u'chinese_aliases']

    return zhwiki_entity_alias


def load_merge_step5_wiki_simplified(dirname, fname):
    merge_step5_wiki_simplified = {}

    name = os.path.join(dirname, fname)
    with codecs.open(name) as fd:
        for line in fd:
            js = json.loads(line.strip())
            for key, value in js.iteritems():
                entity = key[key.rfind('/') + 1:-1]
                if u'resource_alias' in value:
                    merge_step5_wiki_simplified[entity] = value[u'resource_alias']
    return merge_step5_wiki_simplified


def get_all_aliases(entity):
    """
    :param entity: type(entity) is unicode
    """
    if not hasattr(get_all_aliases, '_aliases'):
        dirname = os.path.join(DIR, 'fudankg-json')
        _aliases = {
            'fudan': load_fudankg_alias(dirname),
            'bdbk': load_bdbk_alias(DIR, 'bdbk_entity_alias.json'),
            'zhwiki': load_zhwiki_alias(DIR, 'wikidata_zh.json'),
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
    regchinese = re.compile(u'^[\u4e00-\u9fff]+$')
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


def add_fudan_alias(dirname, fname):
    outfile = os.path.join(dirname, 'zgdbk_entity_with_alias.txt')

    name = os.path.join(dirname, fname)
    with open(name) as fd, codecs.open(outfile, 'w', encoding='utf-8') as wfd:
        for line in fd:
            entity = line.strip().decode('utf-8')
            aliases = get_all_aliases(entity)
            wfd.write(line.strip())
            wfd.write('\t' + '\t'.join(aliases))
            wfd.write('\n')


def human_rule(entity):
    def word_suffix_count():
        counter = collections.Counter()
        input_file = "{}/zgdbk_entities.txt".format(DIR)
        output_file = "{}/lyd_suffix_count.txt".format(DIR)
        with open(input_file, 'r') as f:
            for line in f:
                line = unicode(line.strip(),'utf-8')
                sub1 = line[-1:]
                counter[sub1] += 1
                sub2 = line[-2:]
                counter[sub2] += 1
                sub3 = line[-3:]
                counter[sub3] += 1
        temp = counter.most_common(1000)
        with open(output_file, 'w') as o:
            for t in temp:
                o.write(t[0]+'\t'+str(t[1])+'\n')

    # picked 1000 line from word_suffix_count
    word_list = [u'问题', u'运动', u'县', u'河', u'岛', u'区', u'市',
                 u'自治州', u'城', u'公司', u'技术', u'工程', u'山脉',
                 u'王朝', u'高原', u'研究所', u'共和国', u'古城']
    longer_word_list = [u'股份有限公司', u'运河', u'商城', u'半岛', u'有限公司', u'自然保护区', u'自治县', u'群岛']

    if not isinstance(entity, unicode):
        entity = entity.decode('utf-8')

    for i in itertools.chain(longer_word_list, word_list):
        if entity.endswith(i):
            if i == u'山脉':
                return entity.rstrip(u'脉')
            return entity.rstrip(i)



if __name__ == '__main__':
    add_fudan_alias(DIR, 'zgdbk_entities.txtchinese')
    

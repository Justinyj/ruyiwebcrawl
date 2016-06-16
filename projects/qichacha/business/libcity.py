# encoding=utf-8
import glob
import os
import sys
import json
import collections
import codecs
import re
import hashlib
import datetime
from collections import defaultdict


###################
# global config and functions
def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__))+'/'+filename

gcounter = collections.Counter()

LIST_NATIONAL= [
u'壮族',
u'满族',
u'回族',
u'苗族',
u'维吾尔族',
u'土家族',
u'彝族',
u'蒙古族',
u'藏族',
u'布依族',
u'侗族',
u'瑶族',
u'朝鲜族',
u'白族',
u'哈尼族',
u'哈萨克族',
u'黎族',
u'傣族',
u'畲族',
u'傈僳族',
u'仡佬族',
u'东乡族',
u'高山族',
u'拉祜族',
u'水族',
u'佤族',
u'纳西族',
u'羌族',
u'土族',
u'仫佬族',
u'锡伯族',
u'柯尔克孜族',
u'达斡尔族',
u'景颇族',
u'毛南族',
u'撒拉族',
u'布朗族',
u'塔吉克族',
u'阿昌族',
u'普米族',
u'鄂温克族',
u'怒族',
u'京族',
u'基诺族',
u'德昂族',
u'保安族',
u'俄罗斯族',
u'裕固族',
u'乌孜别克族',
u'门巴族',
u'鄂伦春族',
u'独龙族',
u'塔塔尔族',
u'赫哲族',
u'珞巴族',

u'各族'
]

PATTERN_NATIONAL = u'({})'.format(u'|'.join(LIST_NATIONAL))
PATTERN_NATIONAL2 = u'({})'.format(u'?|'.join([x for x in LIST_NATIONAL if len(x)>2]))

def normalize_national(name):
    temp = name
    temp = re.sub(PATTERN_NATIONAL2,'',temp)
    temp = re.sub(PATTERN_NATIONAL,'',temp)
    return temp


def normalize_province(name):
    name_norm = name

    name_norm = normalize_national(name_norm)
    name_norm = re.sub(ur'(自治区|特别行政区)', '',name_norm)

    name_compact = name_norm
    if len(name_compact)>2:
        name_compact = re.sub(ur'(省|市)$', '',name_compact)
    return [name_norm, name_compact]


def normalize_city(name):
    name_norm = name

    name_norm = normalize_national(name_norm)
    name_norm = re.sub(ur'^(市辖区|自治区直辖县级行政区划|省直辖县级行政区划|矿区|县|区)$', '',name_norm)
    name_norm = re.sub(ur'自治', '',name_norm)

    name_compact = name_norm
    if len(name_compact)>2:
        name_compact = re.sub(ur'(州|地区|市)$', '',name_compact)
    return [name_norm, name_compact]

def normalize_district(name):
    name_norm = name

    name_norm = normalize_national(name_norm)
    name_norm = re.sub(ur'(市辖区|自治|郊区|城区)', '',name_norm)

    name_compact = name_norm
    if len(name_compact)>2:
            name_compact = re.sub(ur'(新区|林区|矿区|区|县|市)$', '',name_compact)
    return [name_norm, name_compact]

class CityData():
    def _get_list_province_unique(self, list_citycode):
        candidates = set()
        for citycode in list_citycode:
            candidates.add( self.data['items'][citycode]['province'])
        if len(candidates)==1:
            [pnorm,pcompact] = normalize_province(list(candidates)[0])
            #print pcompact
            return pcompact

    def __init__(self):
        with open(getTheFile('libcity_cn.json')) as f:
            data = json.load(f)

        self.data ={
            'province':{},
            'city':{},
            'district':{},

            'items':{},
            'alias':{}
        }

        #copy data
        for item in data:
            self.data['items'][item['citycode']] = item

        #process province
        map_province =collections.defaultdict(set)
        set_province =set()
        for item in data:
            p = item.get('province')
            c = item.get('city')
            if p:
                set_province.add(p)
                if not c:
                    map_province[p].add(item['citycode'])
        set_province.difference_update(map_province)
        #print json.dumps(list(set_province), ensure_ascii=False)
        for p in sorted(list(map_province)):
            [pnorm,pcompact] = normalize_province(p)
            self.data['province'][p] = {
                'province': self._get_list_province_unique(map_province[p]),
                'citycode': list(map_province[p]),
                'alias':[p,pnorm,pcompact]}
            map_province[p]=pnorm
            #print json.dumps(list(set([p,pnorm,pnorm2])),ensure_ascii=False)

        #process city
        map_city=collections.defaultdict(set)
        set_city = set()
        for item in data:
            c = item.get('city')
            d = item.get('district')
            if c:
                set_city.add(c)
                if not d:
                    map_city[c].add(item['citycode'])
        set_city.difference_update(map_city)
        #print json.dumps(list(set_city), ensure_ascii=False)
        for p in sorted(list(map_city)):
            [pnorm,pcompact] = normalize_city(p)
            if pnorm:
                #print p, '-->',pnorm, '-->', pcompact
                self.data['city'][p] =  {
                    'province': self._get_list_province_unique(map_city[p]),
                    'citycode': list(map_city[p]),
                    'alias':[p,pnorm,pcompact]}

        #process district
        map_district=collections.defaultdict(set)
        for item in data:
            p = item.get('district')
            if p:
                map_district[p].add(item['citycode'])
        for p in sorted(list(map_district)):
            [pnorm,pcompact] = normalize_district(p)
            if pnorm:
                #print p, '-->',pnorm, '-->', pcompact
                self.data['district'][p] = {
                    'province': self._get_list_province_unique(map_district[p]),
                    'citycode': list(map_district[p]),
                    'alias':[p,pnorm,pcompact]}


        #process duplicated name
        map_alias_code = collections.defaultdict(set)

        for index in ['province','city','district']:
            for name in self.data[index]:
                for alias in self.data[index][name]['alias']:
                    map_alias_code[alias].update(self.data[index][name]['citycode'])

        for alias in map_alias_code:
            if len(map_alias_code[alias])>1:
                #print alias
                for code in set(map_alias_code[alias]):
                    #print json.dumps(self.data['items'][code], ensure_ascii=False)
                    pass

        print "----------"
        for alias in map_alias_code:
            province = self._get_list_province_unique(map_alias_code[alias])
            if province:
                self.data['alias'][alias] = province
            else:
                #print "dup province",alias
                for code in set(map_alias_code[alias]):
                    #print json.dumps(self.data['items'][code], ensure_ascii=False)
                    pass


        #with codecs.open(getTheFile('libcity_cn.new.json'),'w',encoding='utf-8') as f:
        #    json.dump(self.data, f,ensure_ascii=False, indent=4)
        for index in self.data:
            gcounter[index]=len(self.data[index])

        print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

    def stat(self):
        for key in self.data:
            print key, len(self.data[key])

    def guess_province(self, addresses):
        for address in addresses:
            if not address:
                continue
            for index in ['province','city']:
                for name in self.data[index]:
                    for alias in set(self.data[index][name]['alias']):
                        if address.startswith(alias):
                            #print address, '-->', name, self.data[index][name]['province']
                            return  self.data[index][name].get('province')
                        if re.search(ur'（{}）', address):
                            #print address, '-->', name, self.data[index][name]['province']
                            return  self.data[index][name].get('province')

            for alias in self.data['alias']:
                 if address.startswith(alias):
                     return self.data['alias'][alias]
                 if re.search(ur'（{}）'.format(alias), address):
                     return self.data['alias'][alias]

        print 'guess_province failed', json.dumps(addresses, ensure_ascii=False)
        return u""

def test():
    city_data = CityData()
    #city_data.stat()
    print "-----"
    print city_data.guess_province([u"上海西红柿集团"])
    print city_data.guess_provincen([u"浦东新区软件园"])
    print city_data.guess_provincen([u"朝阳新区软件园"])


##################
# main
def show_help():
    print 'invalid input, help not available'

def main():
    #print sys.argv

    if len(sys.argv)<2:
        show_help()
        return

    option= sys.argv[1]

    if 'index' == option:
        index_company_medical()


    elif 'test' == option:
        test()

    else:
        show_help()

if __name__ == '__main__':
    main()
    gcounter[datetime.datetime.now().isoformat()]=1
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

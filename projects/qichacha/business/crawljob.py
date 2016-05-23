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
reload(sys)
sys.setdefaultencoding('utf-8')

from core.qichacha import Qichacha

sys.path.append(os.path.abspath(os.path.dirname(__file__)) )
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import libnlp

###################
# global config and functions
gcounter = collections.Counter()

def getLocalFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/qichacha/","/qichacha/local/") +"/"+filename

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def file2set(filename):
    ret = set()
    with codecs.open(filename,  encoding="utf-8") as f:
        for line in f.readlines():
            line = line.strip()
            #skip comment line
            if line.startswith('#'):
                continue

            if line:
                ret.add(line)
    return ret

def lines2file(lines, filename):
    with codecs.open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line)
            f.write("\n")

def crawl_search(batch, dir_name, refresh=False):
    filenames = glob.glob(dir_name)
    for filename in filenames:
        print filename
        crawl_search_file(batch, filename, refresh)


def crawl_search_file(batch, filename, refresh):
    filename_metadata_search = getLocalFile('crawl_search.{}.json.txt'.format(batch))
    LIMIT = None

    #load prev state
    searched = set()
    if os.path.exists(filename_metadata_search):
        for line in file2set(filename_metadata_search):
            item = json.loads(line)
            searched.update(item["data"].keys())

    #print len(searched),list(searched)[0:3]
    #return

    #add new
    with codecs.open(filename_metadata_search,'a') as flog:
        #crawl_search_pass( FILENAME_CRAWL_SEED_KEYWORDS, searched, flog, crawler.list_corporate_search, LIMIT, False )
        crawl_search_pass( filename, searched, flog, LIMIT, refresh )

def crawl_search_pass( filename, searched, flog, limit, refresh):

    if '_vip' in filename:
        crawler = get_crawler('vip')
    else:
        crawler = get_crawler('regular')

    seeds = file2set(filename)
    counter = collections.Counter()
    counter['total'] = len(seeds)
    counter['searched'] = len(seeds.intersection(searched))
    company_set = set()

    print len(seeds),list(seeds)[0:3]

    for seed in sorted(list(seeds)):
        if counter['visited'] % 10 ==0:
            print os.path.basename(filename), datetime.datetime.now().isoformat(), counter

        counter['visited']+=1
        if not refresh and seed in searched:
            continue
        searched.add(seed)

        print seed, limit
        try:


            if "seed_org" in filename:
                data = crawler.list_corporate_search( [seed], limit)
            elif "seed_person" in filename:
                data = crawler.list_person_search( [seed], limit)
            else:
                print "skip unsupported filename ", fileanme
                continue

            if data:
                item = {
                    "data": data,
                    "ts": datetime.datetime.now().isoformat()
                }

                flog.write(json.dumps(item, ensure_ascii=False))
                flog.write("\n")
            else:
                counter['empty'] +=1

        except:
            counter['failed'] +=1
            pass

    counter['company'] = len(company_set)

    print "final", os.path.basename(filename), counter

    '''
    {
"data": {
    "不孕不育医院": {
        "data": {
            "成都送子鸟不孕不育医院有限公司": {
                "status": "存续",
                "href": "/firm_SC_7b4e0c669165cd33ff04fe8d5af6884d.shtml",
                "name": "成都送子鸟不孕不育医院有限公司",
                "key_num": "7b4e0c669165cd33ff04fe8d5af6884d"
            },
            "洛阳不孕不育症医院（特殊普通合伙企业）": {
                "status": "存续",
                "href": "/firm_HEN_e07d78673eaf2acfa9279adacb0c660e.shtml",
                "name": "洛阳不孕不育症医院（特殊普通合伙企业）",
                "key_num": "e07d78673eaf2acfa9279adacb0c660e"
            }
        },
        "metadata": {
            "total": 58,
            "total_[不孕不育医院][index:2][省:]": 58
        }
    }
},
"ts": "2016-05-22T17:33:47.248311"
}
    '''
def stat(batch):
    all_company = {}
    all_keywords = {}
    filename_metadata_search = getLocalFile('crawl_search.{}.json.txt'.format(batch))
    if os.path.exists(filename_metadata_search):

        for line in file2set(filename_metadata_search):
            gcounter["line"] +=1
            item = json.loads(line)
            for keyword, keyword_entry in item["data"].items():
                #print type(keyword_entry)
                all_company.update(keyword_entry["data"])
                gcounter["all_company_dup"] += len(keyword_entry["data"])
                all_keywords[keyword] = keyword_entry["metadata"]["total_expect2"]
                if keyword_entry["metadata"]["total_expect2"] - keyword_entry["metadata"]["total_actual"]>2:
                    print keyword, json.dumps(keyword_entry["metadata"],ensure_ascii=False)
                else:
                    gcounter["all_keywords_complete"] += 1
                all_keywords[keyword] = keyword_entry["metadata"]["total_expect2"]


    #print json.dumps(all_keywords,ensure_ascii=False)
    gcounter["all_company"] = len(all_company)
    gcounter["all_keywords"] = len(all_keywords)
    all_medical = [x for x in all_company.keys() if libnlp.classify_company_name(x) in [u'医院投资',u'医院公司']]
    gcounter["all_medical"] = len(all_medical)



def merge_company(batch):
    company_name_all = set()
    all_keywords = {}
    #load prev result
    for filename_metadata_search in glob.glob(getLocalFile('company_name*.txt')):
        names = file2set(filename_metadata_search)
        gcounter['company_name_dup1'] += len(names)
        company_name_all.update(names)

    #load from search metadata
    filename_metadata_search = getLocalFile('crawl_search.{}.json.txt'.format(batch))
    for filename in glob.glob(getLocalFile('crawl_search*.json.txt')):
        for line in file2set(filename):
            gcounter["line"] +=1
            item = json.loads(line)
            for keyword, keyword_entry in item["data"].items():
                if 'data' in keyword_entry:
                    names = keyword_entry["data"].keys()
                else:
                    names = keyword_entry.keys()
                gcounter['company_name_dup2'] += len(names)
                company_name_all.update(names)

                if filename == filename_metadata_search:
                    all_keywords[keyword] = keyword_entry["metadata"]["total_expect2"]

    gcounter['company_name_all']=len(company_name_all)
    filename = getLocalFile('company_name.all.txt')
    lines2file(sorted(list(company_name_all)), filename)

    #medical company
    all_medical = [x for x in company_name_all if libnlp.classify_company_name(x) in [u'医院投资',u'医院公司']]
    gcounter["all_medical"] = len(all_medical)
    filename = getLocalFile('company_name.{}.txt'.format(batch))
    lines2file(sorted(list(all_medical)), filename)

    #medical new keywords
    map_name_freq = libnlp.get_keywords(all_medical, None,  100)

    new_keywords = set()
    for name in map_name_freq:
        if not re.match(ur"(医院|公司)$", name):
            name += u"医院"
        new_keywords.update(map_name_freq.keys())

    gcounter["new_keywords_1"] = len(new_keywords)
    new_keywords.difference_update(all_keywords.keys())
    gcounter["new_keywords"] = len(new_keywords)
    filename = getLocalFile('keywords_new.{}.txt'.format(batch))
    lines2file(sorted(list(new_keywords)), filename)

    #medical company


#################

def fetch_detail(batch):

    #load search history
    all_company = {}
    all_keywords = {}
    filename_metadata_search = getLocalFile('crawl_search.{}.json.txt'.format(batch))
    if os.path.exists(filename_metadata_search):

        for line in file2set(filename_metadata_search):
            gcounter["line"] +=1
            item = json.loads(line)
            for keyword, keyword_entry in item["data"].items():
                #print type(keyword_entry)
                all_company.update(keyword_entry["data"])
                gcounter["all_company_dup"] += len(keyword_entry["data"])
                all_keywords[keyword] = keyword_entry["metadata"]["total_expect2"]

    #load names
    print json.dumps(all_company.values()[0], ensure_ascii=False)

    #map names to id
    crawler = get_crawler('regular')
    counter = collections.Counter()
    all_medical = [x for x in all_company.keys() if libnlp.classify_company_name(x) in [u'医院投资',u'医院公司']]
    counter['total'] = len(all_medical)
    for name in all_medical:
        company = all_company[name]
        key_num = company.get('key_num')

        if counter['visited'] % 10 ==0:
            print batch, datetime.datetime.now().isoformat(), counter
        counter['visited']+=1

        try:
            crawler.crawl_company_detail(name, key_num)
            crawler.crawl_descendant_company(name, key_num)
            crawler.crawl_ancestors_company(name, key_num)
            counter['ok'] +=1
        except:
            print "fail", name
            counter['fail'] +=1
            pass


def get_crawler(option):
    filename = getTheFile("../config/conf.179.json")
    with open(filename) as f:
        config = json.load(f)[option]
    return Qichacha(config)

def test():
    seed = "博爱医院"
    crawler = get_crawler('test')
    ret = crawler.list_corporate_search(seed, None)
    print json.dumps(ret, ensure_ascii=False,encoding='utf-8')

def test2():
    seed = "上海华衡投资"
    crawler = Qichacha()
    ret = crawler.list_corporate_search(seed, 1)
    print json.dumps(ret, ensure_ascii=False,encoding='utf-8')

def main():
    #print sys.argv

    if len(sys.argv)<2:
        show_help()
        return

    option= sys.argv[1]
    batch = sys.argv[2]
    #filename = sys.argv[3]
    if "search" == option:
        #crawl_search(batch, getTheFile( batch+"/*"), False)
        crawl_search(batch, getTheFile( batch+"/*_vip*"), True)
        #stat(batch)
        #fetch_detail(batch)


    elif "stat" == option:
        stat(batch)

    elif "merge" == option:
        merge_company(batch)

    elif "fetch" == option:
        fetch_detail(batch)

    elif "test" == option:
        test()
        pass


if __name__ == "__main__":
    main()
    gcounter[datetime.datetime.now().isoformat()]=1
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

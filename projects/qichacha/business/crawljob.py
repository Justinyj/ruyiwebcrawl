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

            if line:
                ret.add(line)
    return ret



def crawl_search(batch):
    dir_name = getTheFile( batch+"/*")
    filenames = glob.glob(dir_name)
    for filename in filenames:
        print filename
        crawl_search_file(batch, filename)


def crawl_search_file(batch, filename):
    filename_metadata_search = getLocalFile('crawl_search.{}.json.txt'.format(batch))
    LIMIT = 100

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
        crawl_search_pass( filename, searched, flog, LIMIT, False )

def crawl_search_pass( filename, searched, flog, limit, refresh):

    crawler = Qichacha()

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

def stat(batch):
    all_company = {}
    filename_metadata_search = getLocalFile('crawl_search.{}.json.txt'.format(batch))
    if os.path.exists(filename_metadata_search):

        for line in file2set(filename_metadata_search):
            gcounter["line"] +=1
            item = json.loads(line)
            gcounter["all_company_dup"] += len(item["data"].values())
            for entry in item["data"].values():
                all_company.update(entry)

    gcounter["all_company"] = len(all_company)


def fetch_detail(batch):

    #load search history
    all_company = {}
    filename_metadata_search = getLocalFile('crawl_search.{}.json.txt'.format(batch))
    if os.path.exists(filename_metadata_search):

        for line in file2set(filename_metadata_search):
            gcounter["line"] +=1
            item = json.loads(line)
            for entry in item["data"].values():
                all_company.update(entry)

    #load names
    print json.dumps(all_company.values()[0], ensure_ascii=False)

    #map names to id
    crawler = Qichacha()
    counter = collections.Counter()
    counter['total'] = len(all_company)
    for company in all_company.values():
        name = company['name']
        key_num = company.get('key_num')

        if counter['visited'] % 10 ==0:
            print batch, datetime.datetime.now().isoformat(), counter
        counter['visited']+=1

        try:
            crawler.crawl_company_detail(name, key_num)
            counter['ok'] +=1
        except:
            print "fail", name
            counter['fail'] +=1
            pass



def test():
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
        crawl_search(batch)
        stat(batch)

    elif "fetch" == option:
        fetch_detail(batch)

    elif "test" == option:
        test()
        pass


if __name__ == "__main__":
    main()
    gcounter[datetime.datetime.now().isoformat()]=1
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

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
import logging
from collections import defaultdict
reload(sys)
sys.setdefaultencoding("utf-8")

from core.qichacha import Qichacha

sys.path.append(os.path.abspath(os.path.dirname(__file__)) )
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

import libnlp
import libfile

###################
# global config and functions
gcounter = collections.Counter()

def getLocalFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/qichacha/","/qichacha/local/") +"/"+filename

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def file2list(filename):
    ret = list()
    visited = set()
    with codecs.open(filename,  encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            #skip comment line
            if line.startswith("#"):
                continue

            if line and line not in visited:
                ret.append(line)
                visited.add(line)
    return ret

def file2set(filename):
    ret = set()
    with codecs.open(filename,  encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            #skip comment line
            if line.startswith("#"):
                continue

            if line and line not in ret:
                ret.add(line)
    return ret

def lines2file(lines, filename):
    with codecs.open(filename, "w", encoding="utf-8") as f:
        for line in lines:
            f.write(line)
            f.write("\n")

def search_count(batch, refresh=False):
    help =""" also try
        python business/crawljob.py search_count medical seed_org_names_reg
        python business/crawljob.py search_count medical seed_person_reg
    """

    if len(sys.argv)>3:
        path_expr = batch+ "/*{}*".format( sys.argv[3])
    else:
        path_expr = batch +"/*"
    dir_name = getTheFile( path_expr )
    print ("search_count on path_expr={}".format(path_expr) +help)

    crawler = get_crawler("regular")

    ret = collections.defaultdict(dict)
    filenames = glob.glob(dir_name)
    for filename in filenames:
        print filename
        seeds = file2set(filename)
        for seed in seeds:
            ret[seed]["name"] = seed
            if "seed_org" in filename:
                indexes = crawler.INDEX_LIST_ORG
                ret[seed]["type"] = "org"
            elif "seed_person" in filename:
                indexes = crawler.INDEX_LIST_PERSON
                ret[seed]["type"] = "person"
            else:
                continue
            total = 0
            for index in indexes:
                cnt = crawler.get_keyword_search_count( seed, index)
                ret[seed]["idx{}".format(index)] = cnt
                total+=cnt
            ret[seed]["total"] = total
            print json.dumps(ret[seed], ensure_ascii=False, sort_keys=True)




def crawl_search(batch, limit=None, refresh=False):
    help = """
        python business/crawljob.py search medical  seed_person_reg
        python business/crawljob.py search medical  seed_org_names_reg
        python business/crawljob.py search medical  _reg
        python business/crawljob.py search medical  _vip
    """
    filename_metadata_search = getLocalFile("crawl_search.{}.json.txt".format(batch))

    if len(sys.argv)>3:
        path_expr = batch+ "/*{}*".format( sys.argv[3])
    else:
        path_expr = batch +"/*"
    dir_name = getTheFile( path_expr )
    print ("search on path_expr={}".format(path_expr) +help)

    filenames = glob.glob(dir_name)
    for filename in filenames:
        print filename

        seeds = file2set(filename)

        searched = set()
        #load prev state if refresh
        if not refresh:
            if os.path.exists(filename_metadata_search):
                for line in file2list(filename_metadata_search):
                    item = json.loads(line)
                    searched.update(item["data"].keys())

        #add new
        with codecs.open(filename_metadata_search,"a") as flog:
            crawl_search_pass( seeds, os.path.basename(filename), searched, flog=flog, limit=limit, refresh=refresh )

def crawl_search_pass( seeds, search_option, searched, flog=None, limit=None, refresh=None):

    #init crawler
    if "_vip" in search_option:
        crawler = get_crawler("vip")
    else:
        crawler = get_crawler("regular")

    if "org" in search_option:
        list_index = crawler.INDEX_LIST_ORG
    elif "person" in search_option:
        list_index = crawler.INDEX_LIST_PERSON
    else:
        print ("skip unsupported search option ", search_option)
        return

    counter = collections.Counter()
    counter["total"] = len(seeds)
    counter["searched"] = len(seeds.intersection(searched))
    company_set = set()

    #print len(seeds),list(seeds)[0:3]

    for seed in sorted(list(seeds)):
        if counter["visited"] % 10 ==0:
            print search_option, datetime.datetime.now().isoformat(), counter

        counter["visited"]+=1
        if not refresh and seed in searched:
            continue
        searched.add(seed)

        print seed, limit
        try:
            data = crawler.list_keyword_search( [seed], list_index, limit=limit, refresh=refresh)

            if data:
                item = {
                    "data": data,
                    "ts": datetime.datetime.now().isoformat()
                }

                if flog:
                    flog.write(json.dumps(item, ensure_ascii=False))
                    flog.write("\n")
            else:
                counter["empty"] +=1

        except:
            import traceback
            traceback.print_exc(file=sys.stdout)
            counter["failed"] +=1
            pass

    counter["company"] = len(company_set)

    print "final", search_option, counter

    """
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
    """
def stat(batch):
    for filename in glob.glob(getLocalFile("crawl_search.{}.json.txt".format(batch))):
        for line in file2list(filename):
            gcounter["line"] +=1
            item = json.loads(line)
            for keyword, keyword_entry in item["data"].items():
                print keyword, len(keyword_entry["data"]), json.dumps(keyword_entry["metadata"])



def load_all_company():
    all_company = {}
    all_keyword = {}
    #all_batch_keyword = collections.defaultdict(dict)

    #load from search metadata
    all_company_temp = set()
    for filename in glob.glob(getLocalFile("crawl_search*.json.txt")):
        batch = os.path.basename(filename).replace("crawl_search.","").replace(".json.txt","")
        for line in file2list(filename):
            gcounter["line"] +=1
            item = json.loads(line)

            for keyword, keyword_entry in item["data"].items():
                if "data" in keyword_entry:
                    company_dict = keyword_entry["data"]
                else:
                    company_dict = keyword_entry

                all_keyword[keyword] = len(keyword_entry)
                all_company.update(company_dict)
                gcounter["company_name_dup_search"] += len(company_dict)

                if keyword in [u"医院"]:
                    #print len(company_dict)
                    all_company_temp.update(company_dict.keys())

    filename_company_temp = getLocalFile("company_temp.txt")
    with codecs.open(filename_company_temp,"w") as f:
        f.write(u"\n".join(all_company_temp))
        f.write(u"\n")


    gcounter["all_company_from_search"] = len(all_company)
    gcounter["all_keyword"] = len(all_keyword)

    #load prev result
    for filename in glob.glob(getLocalFile("company_prev*.txt")):
        names = file2set(filename)
        gcounter["company_name_dup_prev"] += len(names)
        names.difference_update(all_company)
        for name in names:
            if name not in all_company:
                if libnlp.classify_company_name_medical(name, True):
                    print name
                all_company[name]= {"name":name, "key_num":None}

    gcounter["all_company"] = len(all_company)

    #write to text file
    company_name_all = all_company.keys()
    filename = getLocalFile("company_name.all.txt")
    lines2file(sorted(list(company_name_all)), filename)

    #medical company
    company_name_batch = set()
    for x in company_name_all:
        label = libnlp.classify_company_name(x)
        all_company[x]["label"] = label
        gcounter["company_name_{}_label_{}".format(batch, label)] +=1
        if libnlp.classify_company_name_medical(x, True):
            company_name_batch.add(x)

    gcounter["company_name_{}".format(batch)] = len(company_name_batch)
    filename = getLocalFile("company_name.{}.txt".format(batch))
    lines2file(sorted(list(company_name_batch)), filename)

    return (all_company, all_keyword)

def merge_company(batch):

    all_company, all_batch_keyword = load_all_company()

    #medical new keywords
    map_name_freq = libnlp.get_keywords(company_name_batch, None,  100)

    new_keywords = set()
    for name in map_name_freq:
        if not re.match(ur"(医院|公司)$", name):
            name += u"医院"
        new_keywords.update(map_name_freq.keys())

    gcounter["new_keywords_1"] = len(new_keywords)
    new_keywords.difference_update(all_keyword.keys())
    gcounter["new_keywords"] = len(new_keywords)
    filename = getLocalFile("keywords_new.{}.txt".format(batch))
    lines2file(sorted(list(new_keywords)), filename)

    #medical company


#################

def fetch_detail(batch):

    #load search history
    all_company = {}
    all_keyword = {}
    filename_metadata_search = getLocalFile("crawl_search.{}.json.txt".format(batch))
    if os.path.exists(filename_metadata_search):

        for line in file2list(filename_metadata_search):
            gcounter["line"] +=1
            item = json.loads(line)
            for keyword, keyword_entry in item["data"].items():
                #print type(keyword_entry)
                all_company.update(keyword_entry["data"])
                gcounter["all_company_dup"] += len(keyword_entry["data"])
                all_keyword[keyword] = keyword_entry["metadata"]["total_expect2"]

    #load names
    print json.dumps(all_company.values()[0], ensure_ascii=False)
    gcounter["all_company"] += len(all_company)

    #map names to id
    crawler = get_crawler("regular")
    counter = collections.Counter()
    company_name_batch = [x for x in all_company.keys() if libnlp.classify_company_name_medical(x, False)]
    counter["total"] = len(company_name_batch)
    company_raw = {}
    for name in company_name_batch:
        company = all_company[name]
        key_num = company.get("key_num")

        if counter["visited"] % 100 ==0:
            print batch, datetime.datetime.now().isoformat(), counter
        counter["visited"]+=1

        try:
            company_raw_one = {}
            #temp = crawler.crawl_company_detail(name, key_num)
            #company_raw_one.update(temp)

            temp = crawler.crawl_descendant_company(name, key_num)
            company_raw_one.update(temp)

            temp = crawler.crawl_ancestors_company(name, key_num)
            company_raw_one.update(temp)

            company_raw.update(company_raw_one)
            counter["company_raw_one"] =len(company_raw_one)
            counter["company_raw"] =len(company_raw)
            counter["ok"] +=1
        except:
            print "fail", name
            counter["fail"] +=1
            pass

    gcounter["company_raw.{}.json".format(batch)] = len(company_raw)
    filename = getLocalFile("company_raw.{}.json".format(batch))
    with codecs.open(filename,"w", encoding="utf-8") as f:
        json.dump(company_raw, f, ensure_ascii=False, indent=4 )


def expand_person(batch, limit=2):
    filename = getLocalFile("company_raw.{}.json".format(batch))
    with codecs.open(filename, encoding="utf-8") as f:
        company_raw = json.load(f)
        gcounter["company_raw".format(batch)] = len(company_raw)


    filename = getTheFile("{}/seed_person_reg.putian.txt".format(batch))
    root_persons = libfile.file2set(filename)
    gcounter["root_persons".format(batch)] = len(root_persons)
    front_persons = {}
    for name in root_persons:
        front_persons[name]={"depth":0}

    for depth in range(1,limit+1):
        new_front_persons = expand_person_pass(front_persons, company_raw, depth)
        if not new_front_persons:
            break
        front_persons.update(new_front_persons)


def expand_person_pass(front_persons, company_raw, depth):
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

    map_person_coimpact = collections.defaultdict(set)
    for rawitem in company_raw.values():
        name = rawitem["name"]
        #print json.dumps(rawitem,ensure_ascii=False,indent=4, sort_keys=True)

        controllers = libnlp.list_item_agent_name(rawitem, False, ["invests"],None)
        if len(controllers)>500:
            print (json.dumps(["skip too many controllers", name , len(controllers)],ensure_ascii=False))
            continue

        controller_inroot = controllers.intersection(front_persons)
        if len(controller_inroot)<depth:
            continue
        elif len(controller_inroot)<len(controllers)*0.01:
            continue

        for controller in controllers:
            map_person_coimpact[controller].add(name)

    gcounter["map_person_coimpact_depth_{}".format(depth)] = len(map_person_coimpact)

    related_persons = {}
    for name in map_person_coimpact:
        if len(map_person_coimpact[name])<=1:
            continue
        if len(name)>4:
            continue
        if not name in front_persons:
            related_persons[name]={"depth":depth}
            msg =[name, len(map_person_coimpact[name]), list(map_person_coimpact[name])]
            print (json.dumps(msg,ensure_ascii=False))

            related_persons[name]["company"] = map_person_coimpact[name]
        else:
            front_persons[name]["company"] = map_person_coimpact[name]


    gcounter["related_person_depth_{}".format(depth)] = len(related_persons)

    return related_persons







def get_crawler(option):
    filename = getTheFile("../config/conf.x179.json")
    with open(filename) as f:
        config = json.load(f)[option]
    return Qichacha(config)


def test_cookie():

    option = sys.argv[2]

    help ="""
        python business/crawljob.py test_cookie regular
        python business/crawljob.py test_cookie test
        python business/crawljob.py test_cookie vip
    """
    print ("test_cookie with opion="+ option+" .  also try:"+help)

    filename = getTheFile("../config/conf.x179.json")
    with open(filename) as f:
        config = json.load(f)[option]
        config["debug"] = True
    crawler = Qichacha(config)

    seed = "卓国洪"
    index = 14
    province = "ZJ"
    for i in range(0, len(config["COOKIES"])):
        cnt = crawler.get_keyword_search_count( seed, index, refresh=True)
        print cnt
        assert (cnt==6)


def test_parse():
    help ="""  indexmap  2:企业名   4:法人  6:高管  14:股东
        python business/crawljob.py test_count 李国华 4
        python business/crawljob.py test_count 李国华 14
        python business/crawljob.py test_count 李国华 6 FJ
        python business/crawljob.py test_count 医院投资 2
    """

    import lxml
    crawler = get_crawler("test")

    keyword = sys.argv[2] #"李国华"
    page = 0
    index= sys.argv[3] # "6"


def test_count():
    help ="""  indexmap  2:企业名   4:法人  6:高管  14:股东
        python business/crawljob.py test_count 李国华 4
        python business/crawljob.py test_count 李国华 14
        python business/crawljob.py test_count 李国华 6 FJ
        python business/crawljob.py test_count 医院投资 2
    """

    import lxml
    crawler = get_crawler("test")

    keyword = sys.argv[2] #"李国华"
    page = 0
    index= sys.argv[3] # "6"

    if len(sys.argv)>4:
        province= sys.argv[4] # "FJ"
    else:
        province = u""

    print ("test_count with keyword="+ keyword+" .  also try:"+help)

    url = crawler.list_url.format(key=keyword, index=index, page=page, province=province)
    print url

    source = crawler.downloader.access_page_with_cache(url, groups="test")
    #print source
    tree = lxml.html.fromstring(source)
    cnt = crawler.parser.parse_search_result_count(tree)
    print cnt
    assert (int(cnt)>0)

def test_search():
    help ="""  indexmap  2:企业名   4:法人  6:高管  14:股东
        python business/crawljob.py test_search 任丽娟 14 BJ
    """

    import lxml
    crawler = get_crawler("test")

    keyword = sys.argv[2] #"李国华"
    page = 0
    index= sys.argv[3] # "6"

    if len(sys.argv)>4:
        province= sys.argv[4] # "FJ"
    else:
        province = u""

    print ("test_search with keyword="+ keyword+" .  also try:"+help)

    metadata_dict = collections.Counter()
    summary_dict_by_index ={}
    crawler.list_keyword_search_onepass(keyword, index, province, 10, metadata_dict, summary_dict_by_index, refresh=False)
    print len(summary_dict_by_index)
    print json.dumps(metadata_dict)

def test():
    print "test"

def test3():
    seed = "黄钰孙"
    crawler = get_crawler("test")
    ret = crawler.list_person_search(seed, None)
    print json.dumps(ret, ensure_ascii=False,encoding="utf-8")


def test2():
    seed = "博爱医院"
    crawler = get_crawler("test")
    ret = crawler.list_corporate_search(seed, None)
    print json.dumps(ret, ensure_ascii=False,encoding="utf-8")

    seed = "上海华衡投资"
    crawler = Qichacha()
    ret = crawler.list_corporate_search(seed, 1)
    print json.dumps(ret, ensure_ascii=False,encoding="utf-8")

def main():
    #print sys.argv

    if len(sys.argv)<3:
        test()
        return

    option= sys.argv[1]
    batch = sys.argv[2]
    #filename = sys.argv[3]
    if "search" == option:
        crawl_search(batch, refresh=False)

    elif "search_count" == option:
        search_count(batch, refresh=False)



    elif "stat" == option:
        stat(batch)


    elif "fetch" == option:
        fetch_detail(batch)

    elif "expand_person" == option:
        expand_person(batch)

    elif "test" == option:
        test()
        pass



    elif "test_cookie" == option:
        test_cookie()
    elif "test_count" == option:
        test_count()
    elif "test_search" == option:
        test_search()


if __name__ == "__main__":
    main()
    gcounter[datetime.datetime.now().isoformat()]=1
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

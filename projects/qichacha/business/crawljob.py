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


sys.path.append(os.path.abspath(os.path.dirname(__file__)) )
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from core.qichacha2 import Qichacha
from core.cache import Cache
import libnlp
import libfile


###################
# global config and functions
gcounter = collections.Counter()

def getLocalFile(filename):
    return os.path.abspath(os.path.dirname(__file__)).replace("/projects/","/local/") +"/"+filename

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

COOKIE_INDEX_VIP = "vip"
COOKIE_INDEX_SEARCH = "search"
COOKIE_INDEX_FETCH = "fetch"
COOKIE_INDEX_TEST = "test"
COOKIE_INDEX_PREFETCH = "prefetch"
BATCH_ID_SEARCH ='qichacha_search_20160603'
BATCH_ID_FETCH ='qichacha_fetch_20160603'
BATCH_ID_JSON ='qichacha_json_20160603'
BATCH_ID_JSON_SEARCH ='qichacha20160607jsonsearch'
FILE_CONFIG = getTheFile("../config/conf.fs.json")


######################### init
def init_dir(batch):
    filenames = [
        getLocalFile("input"), #on my machine, up to client and server
        getLocalFile("work"), #on my machine, up to client and server
        getLocalFile("client"), #down from web client
        getLocalFile("server"), #down from web server
        getLocalFile("output"), #on my machine, share by other project
        getLocalFile("temp"),   #everyone, no sync
    ]
    for filename in filenames:
        try:
            print os.makedirs(filename)
        except:
            pass

def get_filename_search_index(batch):
    return getLocalFile("server/search_index.{}.json.txt".format(batch))

def stat(batch):
    #load list
    map_step = {
        u"莆田系关键人": {"filename":getTheFile("{}/seed_person_core_reg.putian.human.txt".format(batch))},
        u"莆田系相关人": {"filename":getTheFile("{}/seed_person_ext_reg.putian.human.txt".format(batch))},
        u"医疗类公司关键词": {"filename":getTheFile("{}/seed_org_keywords_vip.putian.human.txt".format(batch))},
    }
    for step in map_step:
        temp = libfile.file2set(map_step[step]["filename"])
        gcounter[step+u"_cnt_keywords"] = len(temp)
        map_step[step]["keyword_list"] = sorted(list(temp))

    #load search result file
    filename_search_index =get_filename_search_index(batch)

    #load prev state if refresh
    search_index = _get_search_index(filename_search_index)
    gcounter[u"total_keywords"] = len(search_index)

    # step actual
    for step in map_step:
        print u"=========keywords {}".format(step)
        temp_company = collections.defaultdict(set)
        for keyword in map_step[step]["keyword_list"]:
            if not keyword in search_index:
                print "missing", keyword, step
                continue

            print "{}\t{}\t{}".format(keyword, search_index[keyword]["metadata"]["expect"], search_index[keyword]["metadata"]["actual"])

            #stype = search_index[keyword]["stype"]
            #uri = _get_search_keyword_uri(stype, keyword)
            #map_company = _get_json(cralwer.config, batch, uri)

        #     for company_name in map_company.keys():
        #         temp_company[step+u"_公司"].add(company_name)
        #         label = libnlp.classify_company_name(company_name)
        #         temp_company[step+u"_公司_"+label].add(company_name)
        #
        # for key in temp_company:
        #     gcounter[key] = len(temp_company[key])
        # map_step[step]["company_list"] = sorted(list(temp_company[step+u"_公司"]))




######################### search
def _get_search_index(filename_search_index):
    #init searched
    search_index = {}
    if os.path.exists(filename_search_index):
        for line in libfile.file2list(filename_search_index):
            item = json.loads(line)
            keyword = item["keyword"]
            search_index[keyword]=item
    gcounter["searched_keywords"]= len(search_index)
    return search_index

def _get_search_keyword_uri(stype, keyword):
    return u"uri:search:{}:keyword:{}".format(stype, keyword)

def _get_json(config, batch_id, uri):
    cache_json = Cache(config, batch_id=batch_id)
    content = cache_json.get(uri)
    if content:
        return json.loads(content)

def _put_json(config, batch_id, uri, data):
    if data:
        cache_json = Cache(config, batch_id=batch_id)
        cache_json.post(uri, json.dumps(data))

def crawl_search(batch, path_expr, limit=None, refresh=False, worker_id=None, cookie_index=COOKIE_INDEX_SEARCH):
    help = """
        #prefetch
        python business/crawljob.py search medical  seed_person_core_reg 0
        python business/crawljob.py search medical  seed_person_ext_reg 0

        # merge
        python business/crawljob.py search medical  seed_person_core_reg
        python business/crawljob.py search medical  seed_person_ext_reg
        python business/crawljob.py search medical  seed_org*_vip
    """
    filename_search_index =get_filename_search_index(batch)

    #load prev state if refresh
    search_index = _get_search_index(filename_search_index) if not refresh else {}
    searched = search_index.keys()

    #print ("search on path_expr={}".format(path_expr) +help)
    dir_name = getTheFile( path_expr )
    filenames = glob.glob(dir_name)
    for filename in filenames:
        print "crawl_search", filename
        seeds = libfile.file2set(filename)
        #add new
        crawl_search_pass( seeds, os.path.basename(filename), searched, filename_search_index=filename_search_index, limit=limit, refresh=refresh, worker_id=worker_id, cookie_index=cookie_index)

def crawl_search_pass( seeds, search_option, searched, filename_search_index=None, limit=None, refresh=None, skip_index_max=None, worker_id=None, cookie_index=None):

    #init crawler
    if "_vip" in search_option:
        crawler = get_crawler(BATCH_ID_SEARCH, COOKIE_INDEX_VIP, worker_id=worker_id)
        stype = "vip"
    else:
        crawler = get_crawler(BATCH_ID_SEARCH, cookie_index, worker_id=worker_id)
        stype ="reg"

    if "org" in search_option:
        list_index = crawler.INDEX_LIST_ORG
    elif "person" in search_option:
        list_index = crawler.INDEX_LIST_PERSON
        #!!!!
        skip_index_max=2000
    else:
        print ("skip unsupported search option ", search_option)
        return

    counter = collections.Counter()
    counter["total"] = len(seeds)
    counter["searched"] = len(seeds.intersection(searched))
    company_set = set()
    worker_num = crawler.config.get("WORKER_NUM",1)

    #print len(seeds),list(seeds)[0:3]

    for seed in sorted(list(seeds)):
        if counter["visited"] % 10 ==0:
            print search_option, datetime.datetime.now().isoformat(), counter

        counter["visited"]+=1
        if not refresh and seed in searched:
            counter["skipped_cache"]+=1
            continue
        searched.add(seed)

        if worker_id is not None and worker_num>1:
            if (counter["visited"] % worker_num) != worker_id:
                counter["skipped_peer"]+=1
                continue

        #print seed, limit
        try:
            data = crawler.list_keyword_search( [seed], list_index, limit=limit, refresh=refresh, skip_index_max=skip_index_max)

            if not data :
                counter["empty"] +=1
            else:
                counter["ok"] +=1

                #cache search result
                uri = _get_search_keyword_uri(stype, seed)
                _put_json(crawler.config, BATCH_ID_JSON_SEARCH, uri, data[seed])

                #
                if filename_search_index:
                    with codecs.open(filename_search_index,"a") as findex:
                        for name in data:
                            item = {
                                "keyword": name,
                                "metadata": data[name]["metadata"],
                                "stype":stype,
                                "ts": datetime.datetime.now().isoformat()
                            }

                            findex.write(u"{}\n".format(json.dumps(item, ensure_ascii=False)))

        except SystemExit as e:
            print "crawl_search_pass", datetime.datetime.now().isoformat()
            sys.exit(e)
        except:
            import traceback
            traceback.print_exc(file=sys.stdout)
            counter["failed"] +=1
            pass

    counter["company"] = len(company_set)

    print "final", search_option, counter






















def search_count(batch, refresh=False):
    help =""" also try
        python business/crawljob.py search_count medical seed_org_names_reg
        python business/crawljob.py search_count medical seed_person_core_reg
    """

    if len(sys.argv)>3:
        path_expr = batch+ "/*{}*".format( sys.argv[3])
    else:
        path_expr = batch +"/*"
    dir_name = getTheFile( path_expr )
    print ("search_count on path_expr={}".format(path_expr) +help)

    crawler = get_crawler(BATCH_ID_SEARCH, COOKIE_INDEX_SEARCH)

    ret = collections.defaultdict(dict)
    filenames = glob.glob(dir_name)
    for filename in filenames:
        print filename
        seeds = libfile.file2set(filename)
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


def load_all_company():
    all_company = {}
    all_keyword = {}
    #all_batch_keyword = collections.defaultdict(dict)

    #load from search metadata
    all_company_temp = set()
    for filename in glob.glob(getLocalFile("work/crawl_search*.json.txt")):
        batch = os.path.basename(filename).replace("crawl_search.","").replace(".json.txt","")
        for line in libfile.file2list(filename):
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

    filename_company_temp = getLocalFile("temp/company_temp.txt")
    with codecs.open(filename_company_temp,"w") as f:
        f.write(u"\n".join(all_company_temp))
        f.write(u"\n")


    gcounter["all_company_from_search"] = len(all_company)
    gcounter["all_keyword"] = len(all_keyword)

    #load prev result
    for filename in glob.glob(getLocalFile("work/company_prev*.txt")):
        names = libfile.file2set(filename)
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
    filename = getLocalFile("temp/company_name.all.txt")
    libfile.lines2file(sorted(list(company_name_all)), filename)

    #medical company
    company_name_batch = set()
    for x in company_name_all:
        label = libnlp.classify_company_name(x)
        all_company[x]["label"] = label
        gcounter["company_name_{}_label_{}".format(batch, label)] +=1
        if libnlp.classify_company_name_medical(x, True):
            company_name_batch.add(x)

    gcounter["company_name_{}".format(batch)] = len(company_name_batch)
    filename = getLocalFile("temp/company_name.{}.txt".format(batch))
    libfile.lines2file(sorted(list(company_name_batch)), filename)

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
    filename = getLocalFile("temp/keywords_new.{}.txt".format(batch))
    libfile.lines2file(sorted(list(new_keywords)), filename)

    #medical company


def fetch_company_raw(batch, expand=True):
    filename_cache_fetch_result = getLocalFile("server/cache_fetch_result.expand_{}.json.txt".format(expand).lower())
    putian_list = set()

    filenames = [
         getTheFile("{}/seed_person_core_reg.putian.human.txt".format(batch)),
         getTheFile("{}/seed_person_ext_reg.putian.human.txt".format(batch)),
         getTheFile("{}/candidates.putian.human.txt".format(batch)),
    ]
    for filename in filenames:
        temp = libfile.file2set(filename)
        gcounter["from_{}".format(os.path.basename(filename))] = len(temp)
        putian_list.update(temp)

    gcounter["putian_list"] = len(putian_list)
    print json.dumps(gcounter, indent=4)

    #load cache_fetch_result
    #cache_fetch_result = {}
    cached_key_num = {}
    company_raw = {}
    if os.path.exists(filename_cache_fetch_result):
        #may have duplicated, the earlier one will be overwrite by the newer one
        cnt = 0
        with codecs.open(filename_cache_fetch_result,  encoding="utf-8") as f:
            for line in f:
                if cnt %1000 == 0:
                    print datetime.datetime.now().isoformat(), cnt, len(company_raw), len(cached_key_num)
                cnt += 1

                fetch_result = json.loads(line)
                key_num = fetch_result["key_num"]
                name = fetch_result["name"]

                #all data
                for n in fetch_result["data"]:
                    cached_key_num[n]=fetch_result["data"][n]["key_num"]

                #putian candidates
                if name in putian_list:
                    gcounter["candidate_by_name"] +=1
                    company_raw.update(fetch_result["data"])
                else:
                    rawitem = fetch_result["data"][name]
                    if libnlp.is_rawitem_putian_canidate(rawitem, putian_list):
                        gcounter["candidate_by_other"] +=1
                        company_raw.update(fetch_result["data"])


    #print len(cache_fetch_result)
    gcounter["company_raw.candidate.{}.json".format(batch)] = len(company_raw)
    filename = getLocalFile("server/company_raw.candidate.{}.json".format(batch))
    with codecs.open(filename,"w", encoding="utf-8") as f:
        json.dump(company_raw, f, ensure_ascii=False, indent=4, sort_keys=True )

    gcounter["company_all"] =len(cached_key_num)
    lines = [ u"{}\t{}".format(cached_key_num[x], x) for x in sorted(list(cached_key_num.keys())) ]
    filename = getLocalFile("server/company_raw_all.{}.txt".format(batch))
    libfile.lines2file(lines, filename)

#################

def fetch_detail(batch, worker_id=None, expand=True, cookie_index =COOKIE_INDEX_PREFETCH, cache_only=False, refresh=False):
    flag_mono = (worker_id is None)
    filename_cache_fetch_result = getLocalFile("server/cache_fetch_result.expand_{}.json.txt".format(expand).lower())

    #load cache_fetch_result
    if flag_mono:
        #cache_fetch_result = {}
        cached_key_num = set()
        if os.path.exists(filename_cache_fetch_result):
            #may have duplicated, the earlier one will be overwrite by the newer one
            cnt = 0
            with codecs.open(filename_cache_fetch_result,  encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    #skip comment line
                    if line.startswith('#'):
                        continue

                    if cnt %1000 == 0:
                        print cnt, datetime.datetime.now().isoformat()

                    cnt += 1
                    fetch_result = json.loads(line)
                    key_num = fetch_result["key_num"]
                    #cache_fetch_result[key_num] = fetch_result["data"]
                    cached_key_num.add(key_num)
            #print len(cache_fetch_result)

    #load search history
    map_key_num_name_crawl = {}
    all_keyword = {}
    filename_metadata_search = getLocalFile("work/crawl_search.{}.json.txt".format(batch))
    if os.path.exists(filename_metadata_search):

        for line in libfile.file2list(filename_metadata_search):
            gcounter["line"] +=1
            item = json.loads(line)
            for keyword, keyword_entry in item["data"].items():
                #print type(keyword_entry)
                for name in keyword_entry["data"]:
                    company = keyword_entry["data"][name]
                    key_num = company['key_num']
                    map_key_num_name_crawl[key_num] = name

                gcounter["all_company_dup"] += len(keyword_entry["data"])
                all_keyword[keyword] = keyword_entry["metadata"]

    #load names
    gcounter["company_crawl"] += len(map_key_num_name_crawl)

    #load prev company 0531
    map_key_num_name_0531 = {}
    filename = getLocalFile("work/prefetch.0531.raw.tsv".format(batch))
    for line in libfile.file2set(filename):
        key_num,name = line.split('\t',1)
        if name:
            map_key_num_name_0531[key_num] = name

    gcounter["company_0531"] += len(map_key_num_name_0531)
    #merge data
    map_key_num_name_crawl.update(map_key_num_name_0531)

    #map names to id
    crawler = get_crawler(BATCH_ID_FETCH, cookie_index, worker_id = worker_id, cache_only=cache_only)
    cache_json = Cache(crawler.config, batch_id="qichacha_json_20160603")

    counter = collections.Counter()
    company_name_batch = sorted(list(map_key_num_name_crawl.keys()))
    #company_name_batch = [x for x in all_company.keys() if libnlp.classify_company_name_medical(x, False)]
    counter["company_total"] = len(company_name_batch)
    worker_num = crawler.config.get("WORKER_NUM",1)
    company_raw = {}
    company_raw_simple = list()
    for key_num in company_name_batch:
        name = map_key_num_name_crawl[key_num]
        if not name:
            continue

        if counter["visited"] % 1000 ==0:
            counter["company_raw"] =len(company_raw)
            print batch, datetime.datetime.now().isoformat(), json.dumps(counter, sort_keys=True), json.dumps(crawler.downloader.counter, sort_keys=True)
        counter["visited"]+=1

        if worker_id is not None and worker_num>1:
            if (counter["visited"] % worker_num) != worker_id:
                counter["skipped"]+=1
                continue

        #if crawler.config.get("debug"):
        #    print "name",name, "key",key_num

        try:
            company_raw_one = {}
            cache_type = ""

            #三级缓存
            #load cached company_raw_one
            tag = "expand" if expand else "regular"
            cache_json_uri = "uri:qcc:{}:{}".format(tag,key_num)

            if not refresh:
                if flag_mono:
                    if key_num in cached_key_num:
                        gcounter["cached_key_num"]+=1
                        continue
    #                company_raw_one = cache_fetch_result.get(key_num,{})
    #                if company_raw_one:
    #                    cache_type = "local"

                if not company_raw_one:
                    cache_json_content = cache_json.get(cache_json_uri)
                    if cache_json_content:
                        company_raw_one = json.loads(cache_json_content)["data"]
                        cache_type = "json"

            if company_raw_one:
                counter["cached_"+cache_type]+=1
            else:
                if expand:
                    temp = crawler.crawl_descendant_company(name, key_num)
                    if temp:
                        company_raw_one.update(temp)

                    temp = crawler.crawl_ancestors_company(name, key_num)
                    if temp:
                        company_raw_one.update(temp)
                else:
                    temp = crawler.crawl_company_detail(name, key_num)
                    if temp:
                        company_raw_one.update(temp)

                #cache the company_raw_one
                if company_raw_one:
                    fetch_result = {
                        "key_num":key_num,
                        "name": name,
                        "ts": datetime.datetime.now().isoformat(),
                        "data": company_raw_one
                    }
                    cache_json_content = cache_json.post(cache_json_uri, json.dumps(fetch_result))
                    cache_type = ""

            if not company_raw_one:
                gcounter["missing"]+=1
                continue

            #post local cache
            if company_raw_one:
                if flag_mono and cache_type != "local":
                    fetch_result = {
                        "key_num":key_num,
                        "name": name,
                        "ts": datetime.datetime.now().isoformat(),
                        "data": company_raw_one
                    }
                    with codecs.open(filename_cache_fetch_result, 'a',encoding="utf8") as f:
                        f.write(u"{}\n".format(json.dumps(fetch_result)))


            #only create company_raw when it is single threaded OP
            if flag_mono:
                #company_raw.update(company_raw_one)
                #line  = u"{}\t{}".format( company_raw[name]["key_num"], name)
                #company_raw_simple.append(line)
                pass

            #counter["company_raw_one"] =len(company_raw_one)
            counter["ok"] +=1
        except:
            import traceback
            traceback.print_exc(file=sys.stdout)
            #print "fail",
            counter["failed"] +=1
            pass

    #only create company_raw when it is single threaded OP
    #if flag_mono:
        #gcounter["company_raw.{}.json".format(batch)] = len(company_raw)
        # filename = getLocalFile("output/company_raw.{}.json".format(batch))
        # with codecs.open(filename,"w", encoding="utf-8") as f:
        #     json.dump(company_raw, f, ensure_ascii=False, indent=4, sort_keys=True )


        #filename = getLocalFile("output/company_raw.{}.txt".format(batch))
        #libfile.lines2file(company_raw_simple, filename)


#
#
# def prefetch(batch):
#     help ="""
#         python business/crawljob.py prefetch medical
#     """
#     #map names to id
#     crawler = get_crawler(BATCH_ID_FETCH,COOKIE_INDEX_SEARCH)
#     counter = collections.Counter()
#
#
#     #load loaded prefetch urls, will skip them since they have been already submitted
#     filename = getLocalFile("tempprefetch.done.txt".format(batch))
#     if os.path.exists(filename):
#         urls_done = libfile.file2set(filename)
#     else:
#         urls_done =set()
#
#
#     #load prev company 0531
#     urls_0531 = set()
#     filename = getLocalFile("prefetch.0531.raw.tsv".format(batch))
#     for line in libfile.file2set(filename):
#         key_num,name = line.split('\t',1)
#         url = crawler.get_info_url("touzi", key_num, name)
#         urls_0531.add(url)
#
#         url = crawler.get_info_url("base", key_num, name)
#         urls_0531.add(url)
#
#
#     #load search history
#     all_company = {}
#     all_keyword = {}
#     filename_metadata_search = getLocalFile("crawl_search.{}.json.txt".format(batch))
#     if os.path.exists(filename_metadata_search):
#
#         for line in libfile.file2list(filename_metadata_search):
#             gcounter["line"] +=1
#             item = json.loads(line)
#             for keyword, keyword_entry in item["data"].items():
#                 #print type(keyword_entry)
#                 all_company.update(keyword_entry["data"])
#                 gcounter["all_company_dup"] += len(keyword_entry["data"])
#                 all_keyword[keyword] = json.dumps(keyword_entry["metadata"], sort_keys=True).replace("\"","")
#
#     #load names
#     print json.dumps(all_company.values()[0], ensure_ascii=False)
#     gcounter["all_company"] = len(all_company)
#
#     print json.dumps(all_keyword, sort_keys=True, indent=4, ensure_ascii=False)
#
#
#
#     #company_name_batch = [x for x in all_company.keys() if libnlp.classify_company_name_medical(x, False)]
#     company_name_batch = all_company.keys()
#     #gcounter["prefetch_candidate"] = len(all_company)
#     gcounter["prefetch_company_selected"] = len(company_name_batch)
#     urls  = set()
#     for name in company_name_batch:
#         company = all_company[name]
#         key_num = company.get("key_num")
#
#         if counter["visited"] % 1000 ==0:
#             print batch, datetime.datetime.now().isoformat(), counter
#         counter["visited"]+=1
#
#         if "NONAME" in name:
#             name = ""
#
#         url = crawler.get_info_url("touzi", key_num, name)
#         urls.add(url)
#
#         url = crawler.get_info_url("base", key_num, name)
#         urls.add(url)
#
#         #url = crawler.legal_url.format(key_num=key_num, name=name, page=1)
#         #urls.add(url)
#     #urls.update(urls_0531)
#     urls.difference_update(urls_done)
#     gcounter["prefetch_url_actual"] = len(urls)
#
#     gcounter["prefetch.{}.txt".format(batch)] = len(urls)
#     filename = getLocalFile("prefetch.{}.txt".format(batch))
#     libfile.lines2file(sorted(list(urls)), filename)

def expand_person(batch, limit=1):
    #load
    filename = getLocalFile("output/company_raw.{}.json".format(batch))
    with codecs.open(filename, encoding="utf-8") as f:
        company_raw = json.load(f)
        gcounter["company_raw".format(batch)] = len(company_raw)

    #filter medical only
    company_raw_medical = {}
    for rawitem in company_raw.values():
        name = rawitem["name"]

        #print json.dumps(rawitem,ensure_ascii=False,indent=4, sort_keys=True)
        label = libnlp.classify_company_name(name)
        rawitem["info"]["label"] = label
        if not label:
            gcounter["company_raw_skip_label"] += 1
            continue

        controllers = libnlp.list_item_agent_name(rawitem, False, ["invests"],None)
        if len(controllers)>500:
            gcounter["company_raw_skip_500"] += 1
            print (json.dumps(["skip too many controllers", name , len(controllers)],ensure_ascii=False))
            continue

        company_raw_medical[name] = rawitem
        gcounter["company_raw_"+label] += 1

    temp = [company_raw_medical[x]["info"] for x in sorted(list(company_raw_medical)) ]
    filename = getLocalFile("output/company.medical.xls".format(batch))
    libfile.writeExcel(temp, [u"name",u"label",u"address"],filename)


    filename = getTheFile("{}/seed_person_core_reg.putian.human.txt".format(batch))
    root_persons = libfile.file2set(filename)
    gcounter["root_persons".format(batch)] = len(root_persons)
    front_persons = {}
    for name in root_persons:
        front_persons[name]={"depth":0}

    for depth in range(1,limit+1):
        new_front_persons = expand_person_pass(front_persons, company_raw_medical, depth)
        if not new_front_persons:
            break
        print len(new_front_persons)
        front_persons.update(new_front_persons)

    #save list of persons
    seed_person_ext = [x for x in front_persons if x not in root_persons]
    filename = getLocalFile("output/seed_person_ext_reg.putian.auto.txt".format(batch))
    libfile.lines2file(sorted(list(seed_person_ext)), filename )

    seed_person_ext_item = [front_persons[x] for x in sorted(list(front_persons.keys())) if x not in root_persons]
    filename = getLocalFile("output/seed_person_ext_reg.putian.auto.xls".format(batch))
    libfile.writeExcel(seed_person_ext_item, [u"name",u"company_cnt",u"company_list"],filename)

def expand_person_pass(front_persons, company_raw, depth):
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

    map_person_coimpact = collections.defaultdict(set)
    for rawitem in company_raw.values():
        name = rawitem["name"]
        #print json.dumps(rawitem,ensure_ascii=False,indent=4, sort_keys=True)
        controllers = libnlp.list_item_agent_name(rawitem, False, ["invests"],None)
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


        company_inuse = map_person_coimpact[name]
        if len(company_inuse)<2:
            #one hospital invest or two medical
            gcounter["skip-depth{}".format(depth)]+=1
            continue

        if len(name)>4:
            #skip non person
            gcounter["skip-depth{}-non-person".format(depth)]+=1
            continue

        if not name in front_persons:
            related_persons[name]={"depth":depth}
            msg =[name, len(company_inuse), list(company_inuse)]
            print (json.dumps(msg,ensure_ascii=False))

            related_persons[name]["company"] = company_inuse
            related_persons[name]["company_list"] = ",".join(company_inuse)
            related_persons[name]["company_cnt"] = len(company_inuse)
            related_persons[name]["name"] = name
        else:
            front_persons[name]["company"] = company_inuse
            front_persons[name]["company_list"] = ",".join(company_inuse)
            front_persons[name]["company_cnt"] = len(company_inuse)
            front_persons[name]["name"] = name


    gcounter["related_person_depth_{}".format(depth)] = len(related_persons)

    return related_persons




def expand_putian(batch, limit=10):
    #load
    filename = getLocalFile("output/company_raw.{}.json".format(batch))
    with codecs.open(filename, encoding="utf-8") as f:
        company_raw = json.load(f)
        gcounter["company_raw".format(batch)] = len(company_raw)

    #filter medical only
    company_raw_medical = {}
    map_agent_related = collections.defaultdict(set)
    for rawitem in company_raw.values():
        name = rawitem["name"]

        #print json.dumps(rawitem,ensure_ascii=False,indent=4, sort_keys=True)
        label = libnlp.classify_company_name(name)
        rawitem["info"]["label"] = label
        if not label:
            gcounter["company_raw_skip_label"] += 1
            continue

        controllers = libnlp.list_item_agent_name(rawitem, False, ["invests"],None)
        if len(controllers)>500:
            gcounter["company_raw_skip_500"] += 1
            print (json.dumps(["skip too many controllers", name , len(controllers)],ensure_ascii=False))
            continue

        #relation network
        related = libnlp.list_item_agent_name(rawitem, False, None, None)
        map_agent_related[name].update(related)
        for r in related:
            map_agent_related[r].add(name)

        company_raw_medical[name] = rawitem
        gcounter["company_raw_"+label] += 1


    print "company_raw_medical",len(company_raw_medical)
    temp = [company_raw_medical[x]["info"] for x in sorted(list(company_raw_medical)) ]
    filename = getLocalFile("output/company.medical.xls".format(batch))
    libfile.writeExcel(temp, [u"name",u"label",u"address"],filename)

    # init seed persons
    filename = getTheFile("{}/seed_person_core_reg.putian.human.txt".format(batch))
    root_persons = libfile.file2set(filename)
    gcounter["root_persons".format(batch)] = len(root_persons)

    front = {}
    for name in root_persons:
        front[name]={"name":name, "tags":"root","depth":0, "p":0.9, "type": "person", "related_front": []}

    #expand
    for depth in range(1, limit+1):
        new_front = expand_putian_pass(front, company_raw, map_agent_related, depth)
        if not new_front:
            break
        print len(new_front)
        front.update(new_front)

    gcounter["depth_all_related".format(depth)] = len(front)

    related = [front[x] for x in sorted(list(front.keys())) if x not in root_persons]
    filename = getLocalFile("output/related.putian.auto.xls".format(batch))
    libfile.writeExcel(related, [u"name","depth", "p", "type", u"related_cnt",u"related_list"],filename)

    filename = getLocalFile("output/related.putian.auto.json".format(batch))
    libfile.json2file(related, filename)


def expand_putian_pass(front, company_raw, map_agent_related, depth):
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

    front_new = {}
    #expand company
    # >1 shareholder
    map_coimpact = collections.defaultdict(set)
    for name in map_agent_related:
        #print json.dumps(rawitem,i t do tu y=False,indent=4, sort_keys=True)

        related = map_agent_related[name]
        related_front= related.intersection(front)

        if len(related)<2:
            # only one controller
            continue
        elif len(related_front)<len(related)*0.01:
            #too many controller
            continue

        rtype ="company" if len(name)>=4 else "person"
        company = company_raw.get(name)
        label = "na"
        if company:
            rtype = "company"
            label = company["info"]["label"]

        p_not = 1.0
        for namc_cf in related_front:
            p_not *= (1.0-front[namc_cf]["p"])
        p_new = (1.0 - p_not) * 0.8
        p_prev = front.get(name, 0)
        p_max = max(p_new, p_prev)

        if p_max >= 0.7:
            gcounter["depth_{}_0.7_{}".format(depth, rtype)] += 1
            gcounter["depth_{}_0.7_{}".format(depth, label)] += 1
        if p_max >= 0.5:
            gcounter["depth_{}_0.5_{}".format(depth, rtype)] += 1
            gcounter["depth_{}_0.5_{}".format(depth, label)] += 1

        if p_max >= 0.5 and p_new > p_prev :
            info = {
                "name": name,
                "depth":depth,
                "p": p_max,
                "type": rtype,
                "label": label,
                "related_front": sorted(list(related_front)),
                "related_cnt": len(related_front),
                "related_list": ",".join( sorted(list(related_front))),
             }
            if name in front:
                front[name].update(info)
                gcounter["depth_{}_update_front_{}".format(depth, rtype)] += 1
                front[name]["tags"] += "dep{}".format(depth)
            elif name in front_new:
                front_new[name].update(info)
                gcounter["depth_{}_update_front_new_{}".format(depth, rtype)] += 1
                front_new[name]["tags"] += "dep{}".format(depth)
            else:
                front_new[name] = info
                front_new[name]["tags"] = "dep{}".format(depth)
                gcounter["depth_{}_related_{}".format(depth, rtype)] += 1

                #print json.dumps(front_new[name], ensure_ascii=False)
                gcounter["depth_{}_related_{}".format(depth, rtype)] += 1


    return front_new




def get_crawler(batch_id, option, worker_id=None, cache_only=False):
    with open(FILE_CONFIG) as f:
        config = json.load(f)[option]
        if worker_id is not None:
            config['WORKER_ID'] = worker_id
    return Qichacha(config, batch_id, cache_only=cache_only)


def test_cookie(limit=None):

    option = sys.argv[2]

    help ="""
        python business/crawljob.py test_cookie search
        python business/crawljob.py test_cookie test
        python business/crawljob.py test_cookie vip
    """
    print ("test_cookie with opion="+ option+" .  also try:"+help)

    with open(FILE_CONFIG) as f:
        config = json.load(f)[option]
        config["debug"] = True
        config["WORKER_NUM"] =1
        config["CACHE_SERVER"] ="http://52.69.161.139:8000"
        #config["CRAWL_GAP"] =5 *len(config["COOKIES"])
    crawler = Qichacha(config)

    seed = "王健林"
    index = 4
    cookies = collections.defaultdict(dict)
    if limit is None:
        limit = len(config["COOKIES"])
    for i in range(0, limit):
        metadata_dict = collections.Counter()
        summary_dict_onepass = {}
        crawler.list_keyword_search_onepass( seed, index, "", 1, metadata_dict, summary_dict_onepass, True)
        gcounter["list_keyword_search_onepass"] += 1
        cookie = crawler.downloader.get_cur_cookie()

        print json.dumps(metadata_dict, sort_keys=True)
        if not len(summary_dict_onepass) == crawler.NUM_PER_PAGE:
            print "ERROR, BAD COOKIE. max", crawler.NUM_PER_PAGE, "actual", len(summary_dict_onepass)
            group = "bad"
        else:
            group = "good"
        cookies[group][cookie["name"]] = cookie["value"]

    print json.dumps(cookies, sort_keys=True, ensure_ascii=False, indent=4)
    if cookies["bad"]:
        gcounter["bad_cookies"] = len ( cookies["bad"])
    else:
        print "OK, all cookies are great!"

def test_count():
    help ="""  indexmap  2:企业名   4:法人  6:高管  14:股东
        python business/crawljob.py test_count 李国华 4
        python business/crawljob.py test_count 李国华 14
        python business/crawljob.py test_count 李国华 6 FJ
        python business/crawljob.py test_count 医院投资 2
    """


    keyword = sys.argv[2] #"李国华"
    page = 0
    index= sys.argv[3] # "6"

    if len(sys.argv)>4:
        province= sys.argv[4] # "FJ"
    else:
        province = u""

    print ("test_count with keyword="+ keyword+" .  also try:"+help)

    test_count_x(keyword, index, page, province)

def test_count_x(keyword, index, page, province):
    import lxml
    crawler = get_crawler(BATCH_ID_SEARCH, COOKIE_INDEX_TEST)

    url = crawler.list_url.format(key=keyword, index=index, page=page, province=province)
    print url

    source = crawler.downloader.access_page_with_cache(url, groups="test", refresh=False)
    print source
    tree = lxml.html.fromstring(source)
    cnt = crawler.parser.parse_search_result_count(tree)
    print cnt
    assert (int(cnt)>0)

def test_cache_get(keyword, index, page, province):
    import lxml
    crawler = get_crawler(BATCH_ID_SEARCH, COOKIE_INDEX_TEST)

    url = crawler.list_url.format(key=keyword, index=index, page=page, province=province)
    print url

    source = crawler.downloader.cache.get(url)
    print crawler.downloader.check_content_invalid(source)
    print source
    tree = lxml.html.fromstring(source)
    cnt = crawler.parser.parse_search_result_count(tree)
    print cnt
    assert (int(cnt)>0)


def test_fetch(name, key_num):
    crawler = get_crawler(BATCH_ID_FETCH, COOKIE_INDEX_TEST)

    ret = crawler.crawl_company_detail(name, key_num)
    print json.dumps(ret, ensure_ascii=False, indent=4)



def test_search():
    help ="""  indexmap  2:企业名   4:法人  6:高管  14:股东
        python business/crawljob.py test_search 任丽娟 14 BJ
        python business/crawljob.py test_search 卓伟 6
    """

    import lxml
    crawler = get_crawler(BATCH_ID_SEARCH, COOKIE_INDEX_TEST)

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
    crawler.list_keyword_search_onepass(keyword, index, province, 20, metadata_dict, summary_dict_by_index, refresh=True)
    print len(summary_dict_by_index)
    print json.dumps(metadata_dict)


def test():
    print "test"
    #hit http://www.qichacha.com/search?key=吴永同&index=14&p=1&province=
    #test_cache_get(u"吴文忠", 14, 0, "YN")
    test_fetch(u"苏州远大投资有限公司","36a64ffac2863a8ae6a4edd0dc33b271")


def test3():
    seed = "黄钰孙"
    crawler = get_crawler(BATCH_ID_SEARCH,COOKIE_INDEX_TEST)
    ret = crawler.list_person_search(seed, None)
    print json.dumps(ret, ensure_ascii=False,encoding="utf-8")


def test2():
    seed = "博爱医院"
    crawler = get_crawler(BATCH_ID_SEARCH,COOKIE_INDEX_TEST)
    ret = crawler.list_corporate_search(seed, None)
    print json.dumps(ret, ensure_ascii=False,encoding="utf-8")


def main():
    #print sys.argv

    if len(sys.argv)<3:
        test()
        return

    option= sys.argv[1]
    batch = sys.argv[2]
    #filename = sys.argv[3]
    if "stat" == option:
        print option
        stat(batch)
    elif "init_dir" == option:
        print option
        init_dir(batch)



    elif "search" == option:
        if len(sys.argv)>3:
            path_expr = batch+ "/*{}*".format( sys.argv[3])
        else:
            path_expr = batch +"/*"

        if len(sys.argv)>4:
            worker_id = int(sys.argv[4])
            print "search with prefetch"
            crawl_search(batch, path_expr, refresh=False, worker_id=worker_id, cookie_index=COOKIE_INDEX_PREFETCH)
        else:
            print "search mono"
            crawl_search(batch, path_expr, refresh=False, cookie_index=COOKIE_INDEX_SEARCH)







    elif "search_count" == option:
        search_count(batch, refresh=False)





    elif "fetch" == option:
        if len(sys.argv)>3:
            worker_id = int(sys.argv[3])
            print "fetch with prefetch"
            fetch_detail(batch, worker_id, cookie_index=COOKIE_INDEX_PREFETCH, expand=True)
        else:
            print "fetch mono"
            fetch_detail(batch, None, cookie_index=COOKIE_INDEX_FETCH, expand=True)
    elif "fetch_cache_only" == option:
            print "fetch mono cache_only"
            fetch_detail(batch, None, cookie_index=COOKIE_INDEX_FETCH, expand=True, cache_only=True)
    elif "fetch_company_raw" == option:
            print "fetch company_raw"
            fetch_company_raw(batch, expand=True)

    elif "prefetch" == option:
        prefetch(batch)

    elif "expand_person" == option:
        expand_person(batch)

    elif "expand_putian" == option:
        expand_putian(batch)

    elif "test" == option:
        test()
        pass



    elif "test_cookie" == option:
        limit = None
        if len(sys.argv)>3:
            limit = int(sys.argv[3])
        test_cookie(limit)
    elif "test_count" == option:
        test_count()
    elif "test_search" == option:
        test_search()
    elif "test_fetch" == option:
        test_fetch()


if __name__ == "__main__":
    main()
    gcounter[datetime.datetime.now().isoformat()]=1
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

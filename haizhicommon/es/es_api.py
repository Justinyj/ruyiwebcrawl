# encoding=utf-8
# author  Li Ding
# change log
#     2016-06-15  refactor code with run_esbulk_rows and example code working
# curl -XDELETE -u es_admin:ruyiruyies http://nlp.ruyi.ai:9200/ruyiwebcrawl_zhidaoqa_0626
# curl -XDELETE -u es_ruyi:ruyiruyies http://nlp.ruyi.ai:9200/ruyiwebcrawl_zhidaoqa_0626

import requests
import json
import sys
import os
import os.path
import collections
import codecs
import urllib
import hashlib

INDEX_OPTION_INDEX = "index"
INDEX_OPTION_DELETE = "delete"


def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def test_echo(text):
    print text

def gen_es_id(text):
    #assert question as utf8
    if isinstance(text, unicode):
        text = text.encode('utf-8')
    return hashlib.sha1(text).hexdigest()

def get_esconfig(config_option):
    filename_esconfig = getTheFile("esconfig.{}.json".format(config_option))
    if not os.path.exists(filename_esconfig):
        print "FATAL, cannot find", filename_esconfig
        exit(1)

    with open(filename_esconfig) as f:
        esconfig = json.load(f)
        return esconfig

def run_batch(datasets, es_index, option, argv, esbulk_size=1000):
    print "config esbulk_size",esbulk_size
    if option=="upload-test":
        suffix_esdata = argv[2]
        esconfig = get_esconfig("test")
        batch_upload(esconfig, datasets, suffix_esdata, esbulk_size=esbulk_size)
    elif option=="upload-local":
        suffix_esdata = argv[2]
        esconfig = getTheFile("esconfig.local.json")
        batch_upload(esconfig, datasets,  suffix_esdata, esbulk_size=esbulk_size)
    elif option=="upload-prod":
        suffix_esdata = argv[2]
        esconfig = getTheFile("esconfig.prod.json")
        batch_upload(esconfig, datasets,  suffix_esdata, esbulk_size=esbulk_size)
    elif option=="init-test":
        esconfig = getTheFile("esconfig.test.json")
        batch_init(esconfig, datasets)
    elif option=="init-local":
        esconfig = getTheFile("esconfig.local.json")
        batch_init(esconfig, datasets)
    elif option=="init-prod":
        esconfig = getTheFile("esconfig.prod.json")
        batch_init(esconfig, datasets )
    elif option == "stat":
        batch_stat(datasets)
    else:
        return False
    return True

def batch_init(esconfig, datasets):
    es_index_all = set()
    for dataset in datasets:
        if dataset["es_index"] not in es_index_all:
            print "init index",  dataset["es_index"]

            ret = run_es_search(esconfig,  dataset["es_index"],"" , {})
            print ret
            if ret is None:
                run_es_create_index(esconfig, dataset["es_index"])
                es_index_all.add(dataset["es_index"])

    for dataset in datasets:
        with open(dataset["filepath_mapping"],'r') as f:
            mappings = json.load(f)
        ret = run_es_get_mapping(esconfig,  dataset["es_index"], dataset["es_type"] )
        print ret
        if not ret:
            run_es_create_mapping(esconfig, dataset["es_index"], dataset["es_type"], mappings)

def batch_upload(esconfig, datasets, suffix_esdata, esbulk_size=1000):
    #es_api.do_test('test')
    cnt = collections.Counter()
    for dataset  in datasets:
        if not dataset['filepath'].endswith(suffix_esdata):
            continue

        if not os.path.exists(dataset['filepath']):
            print "ERROR missing file ", dataset['filepath']
            exit(0)

        print "\n... uploading dataset" , json.dumps(dataset, ensure_ascii=False)
        run_esbulk('index', esconfig, dataset["es_index"], dataset["es_type"], dataset["filepath"], cnt, esbulk_size=esbulk_size)

    print "OK all files uploaded"
    print json.dumps(cnt, indent=4)


def batch_stat(datasets):
    #es_api.do_test('test')
    cnt = collections.Counter()

    for dataset in datasets:
        if not os.path.exists(dataset['filepath']):
            print "ERROR missing file ", dataset['filepath']
            exit(0)
        with open (dataset['filepath']) as f:
            for line in f.readlines():
                data = json.loads(line)

                cnt[dataset['filepath']] += 1
                cnt["ES_TYPE:"+dataset['es_type']] += 1
                cnt["_total"] +=  1


    cnt["_total_file"] = len(datasets)

    print "OK all files processed"
    print json.dumps(cnt, indent=4, sort_keys=True, ensure_ascii=False)


def run_es_get_mapping(esconfig, es_index, es_type):
    es_search_url  = '{}/{}/{}/_mapping'.format(esconfig["es_url"], es_index, es_type)
    headers = {
        'content-type': 'application/json',
        'Authorization': esconfig["es_auth"]
    }

    r = requests.get(es_search_url, headers=headers)
    if r:
        data = json.loads(r.content)
        return data

def run_es_search(esconfig, es_index, es_type, params):

    if es_type:
        es_search_url  = '{}/{}/{}/_search?{}'.format(esconfig["es_url"], es_index, es_type, urllib.urlencode(params))
    else:
        es_search_url  = '{}/{}/_search?{}'.format(esconfig["es_url"], es_index, urllib.urlencode(params))
    print "run_es_search", es_search_url

    headers = {
        'content-type': 'application/json',
        'Authorization': esconfig["es_auth"]
    }

    r = requests.get(es_search_url, headers=headers)
    if r:
        data = json.loads(r.content)
        if data:
            return data.get('hits',{}).get('hits',None)


def run_es_delete_query(esconfig, es_index, es_type, es_search_url=None):


    if not es_search_url:
        es_search_url  = '{}/{}/{}/_search?size=1000&fields='.format(esconfig["es_url"], es_index, es_type)
    print es_search_url

    headers = {
        'content-type': 'application/json',
        'Authorization': esconfig["es_auth"]
    }
    print es_search_url

    counter  = collections.Counter()
    while(True):
        r = requests.get(es_search_url, headers=headers)
        data = json.loads(r.content)
        counter["round"]+=1
        print counter["round"], data['hits']['total']

        hits = data['hits']['hits']
        if not hits:
            break

        bulkdelete = []
        for hit in hits:

            #print hit["_id"]
            xdetele = {"delete": {"_index": hit["_index"],"_type": hit["_type"], "_id": hit['_id']}}
            bulkdelete.append(json.dumps(xdetele))

        urlBulk  = '{}/_bulk'.format(esconfig["es_url"])
        text="\n".join(bulkdelete)+"\n\n\n\n"
        es_api_post(esconfig, urlBulk, text)

        #print bulkdelete
        #print rx.content


#  curl -XPOST -u es_admin:ruyiruyies http://floyd.shufangkeji.com:50280/es_web/kids201601
def run_es_create_index(esconfig, es_index):

    url = "{}/{}".format(esconfig["es_url"],es_index)
    es_api_post(esconfig, url, "")

#curl -XPUT -u es_admin:ruyiruyies http://floyd.shufangkeji.com:50280/es_web/kids201601/xmly/_mapping?pretty -d @scripts/kids/mapping.kids.json
def run_es_create_mapping(esconfig, es_index, es_type, mapping_json):

    url = "{}/{}/{}/_mapping?pretty".format(esconfig["es_url"],es_index, es_type)
    es_api_put(esconfig, url, json.dumps(mapping_json) )



def run_esbulk(index_option, esconfig, es_index, es_type, filename_esdata, cnt=None, esbulk_size=1000):

    esbulk_id =  os.path.basename(filename_esdata)
    #print esbulk_id

    if cnt is None:
        cnt = collections.Counter()

    ids = set()
    with codecs.open(filename_esdata) as f:
        esbulk = []
        for line in f.readlines():
            line = line.strip()
            #print line
            esrow = json.loads(line)
            esindex = {index_option: {"_index": es_index, "_type": es_type, "_id": esrow["id"]}}

            if esrow['id'] in ids:
                print "skip duplicate", json.dumps(esrow, ensure_ascii=False)
            ids.add(esrow['id'])

            esbulk.append(json.dumps(esindex))
            #esbulk.append(json.dumps(esrow,ensure_ascii=False).encode("utf-8"))
            esbulk.append(line)
            cnt['total']+=1
            cnt[esbulk_id]+=1


            if cnt[esbulk_id]%esbulk_size==0:
                url = "{}/_bulk".format(esconfig["es_url"])
                text = "\n".join(esbulk)+"\n\n\n\n"
                es_api_post(esconfig, url, text)
                esbulk = []
                print "uploaded", cnt[esbulk_id]

        if esbulk:
            url = "{}/_bulk".format(esconfig["es_url"])
            text = "\n".join(esbulk)+"\n\n\n\n"
            es_api_post(esconfig, url, text)
            esbulk = []
    print len(ids), cnt, "record "+ index_option


def run_esbulk_rows(esrows, index_option, esconfig, dataset):

    if type(esrows) == dict:
        esrows = [ esrows ]

    ids = set()
    esbulk = []
    print len(esrows)
    for esrow in esrows:
        esindex = {index_option: {"_index": dataset['es_index'], "_type": dataset['es_type'], "_id": esrow["id"]}}

        if esrow['id'] in ids:
            print "skip duplicate", json.dumps(esrow, ensure_ascii=False)
        ids.add(esrow['id'])

        esbulk.append(json.dumps(esindex))
        esbulk.append(json.dumps(esrow))

    url = "{}/_bulk".format(esconfig["es_url"])
    text = "\n".join(esbulk)+"\n\n\n\n"
    es_api_post(esconfig, url, text)
    print len(ids), "record "+ index_option



def es_api_post(esconfig, url, text):
    print "post", url
    #print text

    #get search result
    headers = {
        #'content-type': 'application/json',
        "Content-type": "text/html; charset=utf-8",
    }
    if "es_auth" in esconfig:
        headers['Authorization'] =esconfig["es_auth"]
    #print data
    if text:
        r = requests.post(url, data=text,  headers=headers)
    else:
        r = requests.post(url,  headers=headers)

    if r.status_code != 200:
        print r.status_code
        print r.content
        print esconfig
        exit(0)

def es_api_put(esconfig, url, text):
    print "put", url

    #get search result
    headers = {
        #'content-type': 'application/json',
        "Content-type": "text/html; charset=utf-8",
        'Authorization': esconfig["es_auth"]
    }
    #print data
    r = requests.put(url, data=text,  headers=headers)

    if r.status_code != 200:
        print r.status_code
        print r.content
        print esconfig
        exit(0)


def test_upload_local():
    ES_DATASET_CONFIG ={
        "local":[
            {   "description":"缺省答案",
                "es_index":"test_esapi3",
                "es_type":"default",
                "filepath_mapping": getTheFile("default.mapping.json"),
#                "filepath": getWorkFile("default_answers.esdata")
            },
        ]
    }

    items = []
    items.append(
        {
            "id": u"test001",
            "name": u"张三",
            "source": u"百科",
            "source_url": u"http://ruyi.ai/",
            "tags": [u"人物"],
        }
    )

    config_option = "local"
    esconfig = get_esconfig(config_option)
    datasets = ES_DATASET_CONFIG[config_option]

    batch_init(esconfig, datasets)
    #for dataset in datasets:
    #    run_esbulk_rows(items, "index", esconfig, dataset )


def test():
    test_echo("hello world!")

    print "run example:  \n python es_api.py"

    test_upload_local()

    #run_es_delete_query('python/admin/esconfig.test.json', 'test', 'faq')

# python python/admin/es_api.py index python/admin/esconfig.test.json test faq data/longquan/longquan_luntan/xuecheng_qa_by20151228.v20160106.esdata

if __name__ == "__main__":
    print 'Argument List:', str(sys.argv)
    if len(sys.argv) <6:
        test()
        exit(0)

    option = sys.argv[1]
    filename_esconfig = sys.argv[2]
    es_index = sys.argv[3]
    es_type = sys.argv[4]
    filename_esdata = sys.argv[5]

    with open(filename_esconfig) as f:
        esconfig = json.load(f)

    run_esbulk(option, esconfig, es_index, es_type, filename_esdata)

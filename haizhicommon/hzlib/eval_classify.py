#coding=utf-8
import nose
import libdata
import json


def test_good_answer():

    filenames = [
        (getLocalFile("test/test_answer_fail.txt"), 0),
        (getLocalFile("test/test_answer_ok.txt"), 1),
    ]
    all_words = collections.Counter()

    tests = []
    all_query = set()
    for filename, expect in filenames:
        print "=====", filename
        entry = {
            "data":libfile.file2list(filename),
            "expect": expect
        }
        temp = set(entry["data"])
        temp.difference_update(all_query)
        entry["data"] = list(temp)
        all_query.update(entry["data"])
        tests.append(entry)
        #gcounter["from_{}".format(os.path.basename(filename))] = len(entry["data"])

    target_names = [u"不是", u"是百科"]
    libdata.eval_fn(tests, target_names, fn_query_filter, api)
    print json.dumps(gcounter, indent=4, sort_keys=True)




    tests = [
    {"expect_status":"fail", "text":u'きみは可爱ね。', "note":"含有日文"}
    ]


    ret = libdata.strip_chinese_text_0708(text)
    if ret["status"] == "ok":
        libdata.print_json(ret)
        assert(ret["status"] != "ok")
    print text

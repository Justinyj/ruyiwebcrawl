#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import sys
import collections
import codecs
import datetime
import json
import re
import time
import random


def extract_zh(text):
    if text:
        return re.sub(ur"[^\u4E00-\u9FA5]","", text).strip()
    else:
        return text

def strip_good_answer(text):
    m = re.search(ur"[^\u4E00-\u9FA5\\w\\s]", text)
    if m:
        return {"status": "fail", "msg": "skip non-chinese english {}".format(m) }

    return {"status":"ok", "text": text}

class Enum(set):
    def __getattr__(self, name):
        if name in self:
            return name.lower()
        raise AttributeError

def jsonp(query, output):
    jsonp = query.get("callback", query.get("jsonp"))
    if jsonp:
        if type(output) in [list,dict]:
            output =  json.dumps(output, sort_keys=True)
        return "{0}({1})".format(jsonp, output)
    else:
        return output

def json_update_by_copy(json_to, json_from, list_field, flag_incremental):
    for field in list_field:
        if json_from.get(field):
            if flag_incremental:
                if not json_to.get(field):
                   json_to[field] = json_from.get(field)
            else:
                json_to[field] = json_from.get(field)

def any2utf8(data):
    ret = data
    if type(data) is dict:
        ret = {}
        for key in data:
            ret[any2utf8(key)] = any2utf8(data[key])
    elif type(data) is list:
        ret = []
        for item in data:
            ret.append(any2utf8(item))
    elif type(data) is unicode:
        ret = data.encode("utf-8")
    return ret

def print_json(data):
    print json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)

def slack_msg(msg, channel_url = 'https://hooks.slack.com/services/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'):
    import requests
    data={ "text": msg }
    #"https://hooks.slack.com/services/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"
    requests.post(channel_url, data=json.dumps(data))
    print (u"slack msg"+msg)

def items2sample(data, limit=10):
    if isinstance(data, list):
        temp = data
    else:
        temp = list(data)
    random.shuffle(temp)
    return temp[:limit]

def eval_f1(target, predicted, target_names):
    from sklearn import metrics
    print(metrics.classification_report(target, predicted, target_names=target_names))
    print(metrics.confusion_matrix(target, predicted))

def eval_fn(tests, target_names, fn_classify, api_obj=None):
    target = []
    predicted = []
    ts_start = time.time()
    for entry in tests:
        for test in entry["data"]:
            actual = fn_classify(test, api_obj, test_expect=entry["expect"], test_data=test)
            target.append(entry["expect"])
            predicted.append(actual)

    duration =  (time.time() - ts_start) * 1000
    print int(duration), "questions,  millisecond per query:",  duration/len(predicted)
    eval_f1(target, predicted, target_names)

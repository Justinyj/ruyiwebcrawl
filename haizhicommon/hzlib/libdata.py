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

def print_json(data):
    print json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)

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

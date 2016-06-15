#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from gevent import monkey; monkey.patch_all()

import gevent
import gevent.queue
import os

from zhidao.zhidao_scheduler import Scheduler
from es.es_api import get_esconfig, batch_init, run_esbulk_rows

CACHESERVER = 'http://192.168.1.179:8000'
ES_DATASET_CONFIG = {
        "description": "百度知道002",
        "es_index": "zhidao",
        "es_type": "zhidao_faq",
        "filepath_mapping": os.path.abspath(os.path.dirname(__file__)) +"/"+"qa_es_schema.json"
}

QUEUE = gevent.queue.Queue()

def search_questions(qword):
    s = Scheduler.instance(CACHESERVER)
    questions = s.run(qword, gap=3)

    for q in questions:
        answers = q['list_answers']
        if answers:
            q['answers'] = answers[0]['content']

    sendto_es(questions)

def sendto_es(questions):
    esconfig = get_esconfig('local')
    batch_init(esconfig, [ES_DATASET_CONFIG])
    run_esbulk_rows(questions, "index", esconfig, ES_DATASET_CONFIG)


def stream_process():
    while 1:
        qword = QUEUE.get()
        search_questions(qword)
        gevent.sleep(0.1)


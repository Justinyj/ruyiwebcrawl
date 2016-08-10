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

import libfile

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

class SimpleNlp():
    def __init__(self, debug=False):
        self.debug = debug
        #print "<<<<<<<<<<<", debug
        import jieba

        #load text
        words_group =[
            "skip_words_all",
            "skip_words_zhidao",
        ]
        for group in words_group:
            lines = set()
            filename = getTheFile("model/{}.human.txt".format(group))
            lines = libfile.file2set(filename)

            filename_no = getTheFile("model/{}_no.human.txt".format(group))
            if os.path.exists(filename_no):
                lines.difference_update( libfile.file2set(filename_no) )

            temp = set()
            for line in lines:
                temp.add( line.split(" ")[0] )
            #print group, len(temp), filename
            setattr(self, group, temp)
            for word in temp:
                jieba.add_word( word )

        #update skip_word
        skip_words_ext = libfile.file2set(getTheFile("model/skip_words_all_ext.human.txt"))
        self.skip_words_all.update(skip_words_ext)
        print "Number of skip words ", len(self.skip_words_all)

        self.jieba = jieba


    def cut_text(self, text):
        if not isinstance(text, unicode):
            text = text.decode("utf-8")

        return self.jieba.cut(text)

    def detect_skip_words(self, text, skip_words_user=None, skip_words_groups=["skip_words_all"]):
        if not isinstance(text, unicode):
            text = text.decode("utf-8")
            
        ret = self.detect_skip_groups(text, skip_words_user=skip_words_user, skip_words_groups=skip_words_groups)
        #print ret
        if ret  and ( ret[0]["group"] in ["skip_phrase", "skip_words_user" ] or ret[0]["group"] in skip_words_groups ):
            return ret[0]["match"]

        return []


    def detect_skip_groups(self, text, skip_words_user=None, skip_words_groups=["skip_words_all"]):
        m = re.search(u"啪啪啪", text)
        if m:
            return [{
                "group": "skip_phrase",
                "match":[m.group(0)]
            }]

        #print "<<<<<<<<", self.debug
        words = set(self.cut_text(text))
        if self.debug:
            print "detect_skip_words words", json.dumps(list(words), ensure_ascii=False)

        #print json.dumps(list(words), ensure_ascii=False)

        ret = []
        if skip_words_user is not None:
            item = {
                "group": "skip_words_user",
                "match": words.intersection(skip_words_user)
            }
            ret.append(item)
        else:
            for group in skip_words_groups:
                item = {
                    "group": group,
                    "match": list(words.intersection( getattr(self, group) ))
                }
                if item["match"]:
                    ret.append(item)
                    break

        if self.debug:
            print "detect_skip_groups ",json.dumps(ret, ensure_ascii=False)

        if ret and ret[0]["match"]:
            return ret
        else:
            return []

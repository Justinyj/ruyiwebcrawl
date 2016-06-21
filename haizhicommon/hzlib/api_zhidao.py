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
import urllib
import difflib


import libfile
from parsers.zhidao_parser import parse_search_json_v0615

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

class ZhidaoNlp():
    def __init__(self, debug=False):
        self.debug = debug
        import jieba
        words_lists =[
            "skip_words_all",
            "baike_words_white",
            "baike_words_black",
        ]
        for words in words_lists:
            filename = getTheFile("model/{}.human.txt".format(words))

            temp = set()
            for line in  libfile.file2set(filename):
                temp.add( line.split(" ")[0] )
            print words, len(temp)
            setattr(self, words, temp)
            jieba.load_userdict(filename)

        self.jieba = jieba
        import jieba.posseg as pseg
        self.pseg = pseg
        self.debug = False

    def cut_text(self, text):
        if not isinstance(text, unicode):
            text = text.decode("utf-8")

        return self.jieba.cut(text)

    def clean_sentence(self, sentence):
        temp = sentence
        map_punc ={".","。","?","？","!","！",",","，",":","："}
        temp = re.sub(ur"([\u4E00-\u9FA5])\\s?(\.)\\s{0,5}([\u4E00-\u9FA5])","\1。\3",temp)
        return temp

    def detect_skip_words(self, text, skip_words=None):
        words = set(self.cut_text(text))
        if self.debug:
            print "detect_skip_words words", json.dumps(list(words), ensure_ascii=False)
        if skip_words is None:
            skip_words = self.skip_words_all
        ret =  words.intersection(skip_words)
        if self.debug:
            print "detect_skip_words skip_words",json.dumps(list(ret), ensure_ascii=False)
        return ret

    def is_answer_bad(self, answer):
        if not isinstance(answer, unicode):
            answer = answer.decode("utf-8")
        if re.search(ur"？|。。。|\.\.\.|\?", answer):
            return True

        return False

    def is_question_baike(self, question, query_filter=2, debug={}):
        if not isinstance(question, unicode):
            question = question.decode("utf-8")
        if query_filter == 1:
            return self.is_question_baike_0617(question)
        elif query_filter == 2:
            #print question, query_filter
            return self.is_question_baike_0618(question, use_pos = True, debug=debug)
        elif query_filter == 3:
            return self.is_question_baike_0618(question, use_pos = False, debug=debug)
        else:
            return True

    def is_question_baike_0617(self, question):
        if not question:
            return False

        if not isinstance(question, unicode):
            question = question.decode("utf-8")

        question_clean = self.clean_question(question)
        question_clean = re.sub(ur"我[国党们执]","", question_clean)
        if re.search(ur"你|我|几点|爸爸|妈妈", question_clean):
            return False
        elif re.search(ur"什么|最|第一|哪|谁|有没有|几|吗|如何|是|有多|[多最][快慢好坏强高少远长老久]|怎么?样?|啥|？",question):
            return True
        elif re.search(ur"百科|距离|历史|介绍|信息",question):
            return True
        else:
            return False


    def clean_question(self, question):
        question_clean = question
        question_clean = re.sub(ur"你(知道|了解|听说|说|认为|觉得|见过|认识)","", question_clean)
        question_clean = re.sub(ur"你?(告诉|给|跟)我(讲|说|推荐)?",r"", question_clean)
        question_clean = re.sub(u"为何", u"为什么", question_clean)
        #question_clean = re.sub(ur"[向对]你",r"", question_clean)
        return question_clean

    def is_question_baike_0618(self, question, use_pos=True, debug=None):
        if not question:
            return False

        if not isinstance(question, unicode):
            question = question.decode("utf-8")

        #regex filter black
        if re.search(ur"[你我].{0,5}[有会能可敢喜爱去来给拿要]", question):
            return False

        #rewrite question
        question_clean = self.clean_question(question)
        question_clean = re.sub(ur"我[国党们执]","", question_clean)
        question_clean = re.sub(ur"(第一|多少|为何|哪)", r" \1 ", question_clean)

        words = set(self.cut_text(question_clean))

        if use_pos:
            words_pos = set(self.pseg.cut(question_clean))
        detected_black = self.baike_words_black.intersection(words)
        detected_white = self.baike_words_white.intersection(words)

        if debug is not None:
            debug["detected_black"] = list(detected_black)
            debug["detected_white"] = list(detected_white)
            debug["words"] = list(words)
            if use_pos and words_pos:
                debug["words_pos"] = list(words_pos)

        if len(detected_black) > 0:
            return False

        if len(detected_white) > 0:
            # if use_pos and words_pos:
            #     good_words = [word for word, flag in words_pos if flag.startswith("n") ]
            #     #print question_clean, good_words
            #     return len(good_words)>0
            # else:
            return True

        if use_pos and words_pos:
            if len(words)<10:
                # all noun
                for word, flag in words_pos:
                    #if not flag.startswith("n") and flag not in ["a","uj","x","y","t","l"]:
                    if flag in ["r"]:
                        #结尾是动词
                        #if flag in ['v'] and question_clean.endswith(word):
                        #    return True

                        #print word, flag
                        return False

                return True

        return False


class ZhidaoFetch():
    def __init__(self, config={}):
        self.api_nlp = ZhidaoNlp()
        self.config = config
        self.debug = config.get("debug")
        if config:
            from downloader.downloader_wrapper import DownloadWrapper
            self.downloader = DownloadWrapper(self.config["cache_server"], self.config["crawl_http_headers"])

    def parse_query(self,query_unicode, query_parser=0):
        if query_parser == 1:
            qword = u" ".join(self.api_nlp.cut_text(query_unicode))
        else:
            qword = query_unicode

        return qword

    def get_search_url_qword(self,query_unicode, query_parser=0):
        qword = self.parse_query(query_unicode, query_parser=query_parser)

        query_url = "http://zhidao.baidu.com/search/?word={0}".format( urllib.quote(qword.encode("utf-8")) )
        return query_url, qword

    def select_best_qapair_0616(self,search_result_json):
        for item in search_result_json:
            if item["is_recommend"] == 1:
                #Thread(target = post_zhidao_fetch_job, args = (item, ) ).start()
                ret ["best_qapair"] = item
                return ret

    def select_top_n_chat_0621(self, query, search_result_json, num_answers_needed):

        good_answers = []
        bad_answers = []
        result_answers = []

        match_score_threshold = 0.6

        for item in search_result_json:
            #print type(query), type(item["question"])
            discount_skip_word = 0
            if self.api_nlp.detect_skip_words(item["question"]):
                print "did not skip min-gan-ci question"
                # continue

            if self.api_nlp.detect_skip_words(item["answers"]):
                print "did not skip min-gan-ci answers"
                # continue

            match_score = difflib.SequenceMatcher(None, query, item["question"]).ratio()
            item["match_score"] = match_score

            if self.api_nlp.is_answer_bad(item["answers"]):
                bad_answers.append(item)
            else:
                good_answers.append(item)

        for item in sorted(good_answers, key=lambda elem: 0-elem["match_score"]):
            match_score = item["match_score"]
            if match_score >= match_score_threshold and len(result_answers) < num_answers_needed:
                result_answers.append(item)
            else:
                break

        if len(result_answers) < num_answers_needed:
            for item in sorted(bad_answers, key=lambda elem: 0-elem["match_score"]):
                match_score = item["match_score"]
                if match_score >= match_score_threshold and len(result_answers) < num_answers_needed:
                    result_answers.append(item)
                else:
                    break

        return result_answers

    def search_chat_top_n(self,query,num_answers_needed,query_filter=2, query_parser=0):
        result = self.prepare_query(query, query_filter, query_parser)
        if not result:
            return False

        ret = result["ret"]
        query_url = result["query_url"]
        query_unicode = ret["query"]
        if self.api_nlp.is_question_baike( query_unicode , query_filter= query_filter):
            print "not skip query, baike", query_filter,  query_unicode
            # return False

        ts_start = time.time()
        content = self.download(query_url)

        ret ["milliseconds_fetch"] = int( (time.time() - ts_start) * 1000 )

        if content:
            ts_start = time.time()
            search_result_json = parse_search_json_v0615(content)
            ret ["milliseconds_parse"] = int( (time.time() - ts_start) * 1000 )

            answer_item = self.select_top_n_chat_0621(query_unicode, search_result_json, num_answers_needed)
            if answer_item:
                index = 0
                for item in answer_item:
                    ret ["qapair{}".format(index)] = item
                    index += 1
                return ret
            #print json.dumps(search_result_json,ensure_ascii=False)

        return False


    def select_best_qapair_0617(self,query, search_result_json):
        best_item = None
        best_score = 0.4
        best_cnt_like = -1
        for item in search_result_json:
            #print type(query), type(item["question"])
            discount_skip_word = 0
            if self.api_nlp.detect_skip_words(item["question"]):
                print "skip min-gan-ci question"
                continue

            if self.api_nlp.detect_skip_words(item["answers"]):
                print "skip min-gan-ci answers"
                continue

            if self.api_nlp.is_answer_bad(item["answers"]):
                print "skip bad answers"
                continue

            match_score = difflib.SequenceMatcher(None, query, item["question"]).ratio()
            item["match_score"] = match_score
            if self.api_nlp.debug:
                print match_score, discount_skip_word, item["answers"]

            #print query, item["question"] ,match_score, item["cnt_like"]
            this_answer_is_better = False
            if match_score > best_score * 1.5:
                this_answer_is_better = True
            elif match_score > best_score * 0.9 and item["cnt_like"] > best_cnt_like:
                this_answer_is_better = True

            if this_answer_is_better:
                best_item = item
                best_score = match_score
                best_cnt_like = item["cnt_like"]
        return best_item

    def search_chat_best(self,query, query_filter=2, query_parser=0):
        result = self.prepare_query(query, query_filter, query_parser)
        if not result:
            return False

        ret = result["ret"]
        query_url = result["query_url"]
        query_unicode = ret["query"]
        if self.api_nlp.is_question_baike( query_unicode , query_filter= query_filter):
            print "skip query, baike", query_filter,  query_unicode
            return False

        ts_start = time.time()
        content = self.download(query_url)

        ret ["milliseconds_fetch"] = int( (time.time() - ts_start) * 1000 )

        if content:
            ts_start = time.time()
            search_result_json = parse_search_json_v0615(content)
            ret ["milliseconds_parse"] = int( (time.time() - ts_start) * 1000 )

            best_item = self.select_best_qapair_0617(query_unicode, search_result_json)
            if best_item:
                ret ["best_qapair"] = best_item
                return ret
            #print json.dumps(search_result_json,ensure_ascii=False)

        return False

    def prepare_query(self, query, query_filter, query_parser ):
        if not query:
            print "skip query, empty"
            return False

        query_unicode = query
        if not isinstance(query_unicode, unicode):
            query_unicode = query_unicode.decode("utf-8")

        if self.api_nlp.detect_skip_words(query_unicode):
            print "skip bad query, empty"
            return False


        query_unicode = re.sub(u"？$","",query_unicode)
        query_url, qword = self.get_search_url_qword(query_unicode, query_parser)

        ret = {
            "query":query_unicode,
        }

        if query_parser == 1:
            ret["qword"] = qword

        return {"ret":ret, "query_url":query_url}

    def search_baike_best(self,query, query_filter=2, query_parser=0):

        result = self.prepare_query(query, query_filter, query_parser)
        if not result:
            return False

        ret = result["ret"]
        query_url = result["query_url"]
        query_unicode = ret["query"]
        if not self.api_nlp.is_question_baike( query_unicode , query_filter= query_filter):
            print "skip query, not baike", query_filter,  query_unicode
            return False

        ts_start = time.time()
        content = self.download(query_url)
        ret ["milliseconds_fetch"] = int( (time.time() - ts_start) * 1000 )


        if content:
            ts_start = time.time()
            search_result_json = parse_search_json_v0615(content)
            ret ["milliseconds_parse"] = int( (time.time() - ts_start) * 1000 )

            best_item = self.select_best_chat_0621(query_unicode, search_result_json)
            if best_item:
                ret ["best_qapair"] = best_item
                return ret
            #print json.dumps(search_result_json,ensure_ascii=False)

        return False

    def download(self, query_url):
        if self.config:
            return self.downloader.download_with_cache(
                    query_url,
                    self.config["batch_id"],
                    self.config["crawl_gap"],
                    self.config["crawl_http_method"],
                    self.config["crawl_timeout"],
                    encoding=None,
                    redirect_check=True,
                    error_check=False,
                    refresh=False)
        else:
            return self.download_direct(query_url)

    def download_direct(self, query_url):
        import requests
        #print query_url
        encoding='gb18030'
        headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': 1,
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
        }
        headers["Host"] = "zhidao.baidu.com"

        print query_url
        r = requests.get(query_url, timeout=10, headers=headers)

        if r:
            r.encoding = encoding
            return r.text

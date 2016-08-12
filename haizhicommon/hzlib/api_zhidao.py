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
#import distance

import libfile
from parsers.zhidao_parser import parse_search_json_v0707

def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

class ZhidaoNlp():
    def __init__(self, debug=False):
        self.debug = debug
        #print "<<<<<<<<<<<", debug
        import jieba

        #load text
        words_lists =[
            "skip_words_all",
            "skip_words_zhidao",
            "baike_words_white",
            "baike_words_black",
        ]
        for words in words_lists:
            lines = set()
            filename = getTheFile("model/{}.human.txt".format(words))
            print filename
            lines = libfile.file2set(filename)

            filename_no = getTheFile("model/{}_no.human.txt".format(words))
            if os.path.exists(filename_no):
                lines.difference_update( libfile.file2set(filename_no) )

            temp = set()
            for line in lines:
                temp.add( line.split(" ")[0] )
            print words, len(temp)
            setattr(self, words, temp)
            for word in temp:
                jieba.add_word( word )

        #update skip_word
        skip_words_ext = libfile.file2set(getTheFile("model/skip_words_all_ext.human.txt"))
        self.skip_words_all.update(skip_words_ext)
        print "Number of skip words ", len(self.skip_words_all)

        self.jieba = jieba
        import jieba.posseg as pseg
        self.pseg = pseg



    def cut_text(self, text):
        if not isinstance(text, unicode):
            text = text.decode("utf-8")

        return self.jieba.cut(text)

    def clean_sentence(self, sentence):
        temp = sentence
        #map_punc ={".":"。",  "?":"？", "!":"！", ",":"，",  ":":"："}
        temp = re.sub(ur"([\u4E00-\u9FA5])\\s?(\.)\\s{0,5}([\u4E00-\u9FA5])","\1。\3",temp)
        return temp

    def detect_skip_words(self, text, skip_words=None, check_list=["skip_words_all"]):
        ret = self.detect_skip_groups(text, skip_words=skip_words, check_list=check_list)
        #print ret
        if ret  and ( ret[0]["group"] in ["skip_phrase" ] or ret[0]["group"] in check_list ):
            return ret[0]["match"]

        return []


    def detect_skip_groups(self, text, skip_words=None, check_list=["skip_words_all"]):
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
        if skip_words is not None:
            item = {
                "group": "skip_words_user",
                "match": words.intersection(skip_words)
            }
            ret.append(item)
        else:
            for group in check_list:
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

    def get_answer_filter_word(self, answer):
        if not isinstance(answer, unicode):
            answer = answer.decode("utf-8")
        m = re.search(ur"？|[。、，！？·；]{2,100}|[我][是想和有的要也]|\.\.\.|\?", answer)
        if m:
            return m.group(0)

        return False

    def is_question_baike(self, question, query_filter=2, debug_item={}):
        if not isinstance(question, unicode):
            question = question.decode("utf-8")
        if query_filter == 1:
            return self.is_question_baike_0617(question)
        elif query_filter == 2:
            #print question, query_filter
            return self.is_question_baike_0618(question, use_pos = True, debug_item=debug_item)
        elif query_filter == 3:
            return self.is_question_baike_0618(question, use_pos = False, debug_item=debug_item)
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

    def filter_chat(self, q, a):
        qa = q+a

        a_zh = a
        a_zh = re.sub(ur"[^\u4E00-\u9FA5]","", a_zh)
        a_zh = re.sub(ur"[，。？！；：]","", a_zh)
        if len(a_zh) < 2:
            return u"外文"

        return False

    def get_chat_label(self, q, a):
        qa = q+a
        map_data = {"skip_phrase": "词组", "skip_words_all": "敏感", "skip_words_zhidao": "知道" }
        ret = self.detect_skip_groups(qa, check_list=["skip_words_zhidao", "skip_words_all"])
        if ret:
            return u"{}:{}".format(map_data.get(ret[0]["group"]),u",".join(ret[0]["match"]))

        #if re.search(ur"[这那谁]一?[个是]+",q):
        #    return u"指代"

        #if re.search(ur"[？！。\?\!][\u4E00-\u9FA5]",q):
        #    return u"断句"


        return u""

    def rewrite_zhidao_query(self, question):
        question_clean = question
        question_clean = re.sub(ur"^你?[有是否没能可以不]*(知道|听说过?|认为|觉得|见过|介绍一?下?|认识|告诉我?)","", question_clean)
        question_clean = re.sub(ur"^你?(给|跟)我(讲|说)*",r"", question_clean)
        question_clean = re.sub(u"为[何啥]子?", u"为什么", question_clean)
        question_clean = re.sub(u"在那里?$", u"在哪里$", question_clean)
        return question_clean

    def clean_question(self, question):
        question_clean = question
        question_clean = question_clean.lower()
        question_clean = re.sub(ur"你(知道|了解|听说|说|认为|觉得|见过|认识)","", question_clean)
        question_clean = re.sub(ur"你?(告诉|给|跟)我(讲|说|推荐)?",r"", question_clean)
        question_clean = re.sub(u"为何", u"为什么", question_clean)
        question_clean = re.sub(u"[“”]", u"", question_clean)
        #question_clean = re.sub(ur"[向对]你",r"", question_clean)
        return question_clean



    def is_question_baike_0618(self, question, use_pos=True, debug_item=None):
        if not question:
            if debug_item is not None:
                debug_item['note']= u"[-]问题空"
            return False

        if not isinstance(question, unicode):
            question = question.decode("utf-8")

        #regex filter black
        m = re.search(ur"[你我].{0,5}[有会能可敢喜爱去来给拿要]", question)
        if m:
            if debug_item is not None:
                debug_item['note']= u"[-]闲聊:{}".format( m.group(0) )
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

        if debug_item is not None:
            debug_item["detected_black"] = list(detected_black)
            debug_item["detected_white"] = list(detected_white)
            debug_item["words"] = list(words)
            if use_pos and words_pos:
                temp = []
                for word,flag in words_pos:
                    temp.append(u"{}[{}]".format(word,flag))
                debug_item["words_pos"] = temp

        if len(detected_black) > 0:
            if debug_item is not None:
                debug_item['note']= u"[-]黑名单:{}".format( u"/".join(detected_black) )
            return False

        if len(detected_white) > 0:
            if debug_item is not None:
                debug_item['note']= u"[+]白名单:{}".format( u"/".join(detected_white) )
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
                        if debug_item is not None:
                            debug_item['note']= u"[-]词性指代:{}".format( u"/".join( debug_item["words_pos"] ) )
                        return False

                if debug_item is not None:
                    debug_item['note']= u"[+]词性名词:{}".format( u"/".join( debug_item["words_pos"] ) )
                return True

        if debug_item is not None:
            debug_item['note']= u"[-]其他"
        return False

    def select_qapair_0624(self, query, search_result_json, result_limit=3, answer_len_limit=100, question_len_limit=30, question_match_limit=0.3):
        result_answers = []

        for item in search_result_json:
            if "answers" not in item:
                item["debug_note"]= u"[-]无答案"
                continue

            #too long question
            if len(item["question"]) > question_len_limit:
                item["debug_note"]= u"[-]问题长度过长:{}".format(len(item["question"]) )
                #print "skip question_len_limit", len(item["question"])
                continue

            #skip long answers
            if len(item["answers"]) > answer_len_limit:
                item["debug_note"]= u"[-]答案长度过长:{}".format(len(item["answers"]) )
                #print "skip answer_len_limit", type(item["answers"]), len(item["answers"]), item["answers"]
                continue

            if len(item["answers"]) < 2:
                item["debug_note"]= u"[-]答案长度过短:{}".format(len(item["answers"]) )
                continue

            if self.filter_chat(item["question"], item["answers"]):
                item["debug_note"]= u"[-]是闲聊"
                continue


            question_match_score = difflib.SequenceMatcher(None, query, item["question"]).ratio()
            answer_match_score   = difflib.SequenceMatcher(None, query, item["answers"]).ratio()
            item["match_score"] = question_match_score
            item["match_score_answers"] = answer_match_score
            item["qa_label"] = self.get_chat_label(item["question"], item["answers"])

            #skip not matching questions
            if (question_match_score < question_match_limit):
                #print "skip question_match_limit", question_match_score
                item["debug_note"]= u"[-]问题匹配度低: ％1.2f" % question_match_score
                continue

            result_answers.append(item)

        ret = sorted(result_answers, key= lambda x: 0 - x["match_score"] )
        if len(ret) > result_limit:
            ret = ret[:result_limit]
#        if len(ret) == 0:
#            for item in search_result_json:
#                print u"{} | {} | {} | {} | {} | {}".format(query, item["question"], item.get("answers"), item.get("label"), item.get("match_score"), item.get("match_score_answers"))
#                print json.dumps(item, ensure_ascii=False)
        return ret

class ZhidaoFetch():
    def __init__(self, config={}):
        self.debug = config.get("debug")
        self.api_nlp = ZhidaoNlp(self.debug)
        self.config = config
        if config:
            from downloader.downloader_wrapper import DownloadWrapper
            print self.config
            self.downloader = DownloadWrapper(self.config.get("cache_server"), self.config["crawl_http_headers"])

    def parse_query(self,query_unicode, query_parser=0):
        if query_parser == 1:
            qword = u" ".join(self.api_nlp.cut_text(query_unicode))
        else:
            qword = query_unicode

        return qword

    def get_search_url_qword(self,query_unicode, query_parser=0, page_number=0):
        qword = self.parse_query(query_unicode, query_parser=query_parser)

        if page_number == 0:
            query_url = "http://zhidao.baidu.com/search/?word={0}".format( urllib.quote(qword.encode("utf-8")) )
        else:
            query_url = "http://zhidao.baidu.com/search/?pn={}&word={}".format( page_number*10, urllib.quote(query) )

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

            if self.api_nlp.get_answer_filter_word(item["answers"]):
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



    def select_top_n_chat_0622(self, query, search_result_json, result_limit=3, answer_len_limit=30, question_len_limit=20, question_match_limit=0.4):
        result_answers = []

        for item in search_result_json:
            if "answers" not in item:
                continue

            #skip long answers
            if len(item["answers"]) > answer_len_limit:
                #print "skip answer_len_limit", type(item["answers"]), len(item["answers"]), item["answers"]
                continue

            #too long question
            if len(item["question"]) > question_len_limit:
                #print "skip question_len_limit", len(item["question"])
                continue

            if self.api_nlp.filter_chat(item["question"], item["answers"]):
                continue

            question_match_score = difflib.SequenceMatcher(None, query, item["question"]).ratio()
#            question_match_score_b = difflib.SequenceMatcher(None,  item["question"], query).ratio()
            item["match_score"] = question_match_score
            item["label"] = self.api_nlp.get_chat_label(item["question"], item["answers"])

            #skip not matching questions
            if (question_match_score < question_match_limit):
                #print "skip question_match_limit", question_match_score
                continue

            result_answers.append(item)

        ret = sorted(result_answers, key= lambda x: 0 - x["match_score"])
        if len(ret) > result_limit:
            ret = ret[:result_limit]
        return ret


    def search_chat_top_n(self,query,num_answers_needed=3,query_filter=2, query_parser=0, select_best=True):
        result = self.prepare_query(query, query_filter, query_parser, use_skip_words=False)
        if not result:
            return False

        ret = result["ret"]
        query_url = result["query_url"]
        query_unicode = ret["query"]
        #if self.api_nlp.is_question_baike( query_unicode , query_filter= query_filter):
        #    print "not skip query, baike", query_filter,  query_unicode
            # return False
        #print query

        ts_start = time.time()
        content = self.download(query_url)

        ret ["milliseconds_fetch"] = int( (time.time() - ts_start) * 1000 )
        if content:
            ret ["content_len"] = len(content)
            #print type(content)
            #print content

        if select_best and content:
            ts_start = time.time()
            search_result = parse_search_json_v0707(content)
            search_result_json = search_result["results"]
            ret ["milliseconds_parse"] = int( (time.time() - ts_start) * 1000 )
            ret ["item_len"] = len(search_result_json)

            answer_items = self.select_top_n_chat_0622(query_unicode, search_result_json, num_answers_needed)
            #print "select_best", len(answer_items)
            ret ["items"] = answer_items
            ret ["results"] = search_result_json
            ret ["total"] = search_result["total"]
            # if answer_items:
            #     index = 0
            #     for item in answer_items:
            #         ret ["qapair{}".format(index)] = item
            #         index += 1
            #     return ret
            #print json.dumps(search_result_json,ensure_ascii=False)

        return ret

    # def text2bigram(self, text):
    #     ret = set()
    #     if not text:
    #         return ret
    #     text = text.lower()
    #     symbols = list(self.api_nlp.cut_text(text))
    #
    #     for i in range(len(symbols)):
    #         if i==0:
    #             word = u'___{}'.format(symbols[i])
    #             ret.add(word)
    #             word = text[i:i+2]
    #             ret.add(word)
    #         elif i == len(text)-1:
    #             word = u'{}___'.format(symbols[i])
    #             ret.add(word)
    #         else:
    #             word = u"".join(symbols[i:i+2])
    #             ret.add(word)
    #     return ret
    #
    # def bigram_sim(self, q1, q2):
    #     b1 = self.text2bigram(q1)
    #     b2 = self.text2bigram(q2)
    #     b1 = set(self.api_nlp.cut_text(q1.lower()))
    #     b2 = set(self.api_nlp.cut_text(q2.lower()))
    #     b1d = set(b1)
    #     b1d.difference_update(b2)
    #
    #     sim = 1.0 * len(b1.intersection(b2))/ len(b1.union(b2))
    #     return sim
    def sim(self, q1, q2):
        q1 = self.api_nlp.clean_question(q1)
        q2 = self.api_nlp.clean_question(q2)
        match_score = difflib.SequenceMatcher(None, q1, q2).ratio()
        return match_score


    def select_best_qapair_0630(self,query, search_result_json, question_len_max=30, answer_len_max=90, answer_len_min=2 ):
        best_item = None
        best_score = 0.6
        best_cnt_like = -1
        used_skip_sources = list()
        for item in search_result_json:
            print json.dumps(item, ensure_ascii=False)
            print "\n\n--------select_best_qapair_0630 "


            if item["source"] in ["muzhi"]:
                used_skip_sources.append( item["source"] )

                item["debug_note"] = u"[-]问答对－来自拇指"
                continue

            #match_score = self.bigram_sim(query, item["question"])
            match_score = self.sim( query, item["question"])
            item["match_score"] = match_score

            #print type(query), type(item["question"])
            temp = self.api_nlp.detect_skip_words(item["question"])
            if temp:
                print "skip min-gan-ci question", json.dumps(list(temp), ensure_ascii=False)
                item["debug_note"] = u"[-]问答对－问题敏感词:{}".format( u"/".join( temp ))
                continue

            temp = self.api_nlp.detect_skip_words(item["answers"], check_list=["skip_words_zhidao", "skip_words_all"])
            if temp:
                print "skip min-gan-ci answers", json.dumps(list(temp), ensure_ascii=False)
                item["debug_note"] = u"[-]问答对－答案敏感词:{}".format( u"/".join( temp ))
                continue

            #too long question
            #if len(item["question"]) > question_len_max:
            #    item["debug_note"]= u"[-]问题长度过长:{}".format(len(item["question"]) )
            #    continue


            if len(item["answers"]) < answer_len_min:
                item["debug_note"]= u"[-]答案长度过短:{}".format(len(item["answers"]) )
                continue

            filter_word =  self.api_nlp.get_answer_filter_word(item["answers"])
            if filter_word:
                print "skip bad answers"
                item["debug_note"] = u"[-]问答对－答案有符号:{}".format(filter_word)
                continue

            if self.api_nlp.debug:
                print match_score, item["answers"]

            #print query, item["question"] ,match_score, item["cnt_like"]
            this_answer_is_better = False
            if item["source"] == "baike":
                item["debug_note"] = u"[+]问答对－使用百科"
                this_answer_is_better = True
            elif not best_item or best_item["source"] != "baike":
                #skip long answers
                #if len(item["answers"]) > answer_len_max and item["cnt_like"] < 50:
                #    item["debug_note"]= u"[-]答案长度过长:{}".format(len(item["answers"]) )
                #    continue

                if match_score > best_score and item["cnt_like"] >= best_cnt_like*0.2:
                    this_answer_is_better = True
                elif match_score > best_score * 0.95 and item["cnt_like"] > best_cnt_like*1.5 + 2:
                    this_answer_is_better = True

            if this_answer_is_better:
                best_item = item
                best_score = max(match_score, best_score)
                best_cnt_like = item["cnt_like"]
                if not item.get("debug_note"):
                    item["debug_note"] = u"[?]问答对－maybe best={}".format( best_score )
            else:
                if not item.get("debug_note"):
                    item["debug_note"] = u"[-]问答对－低于best={}".format( best_score )

        if best_item and best_item["source"] not in ["baike"] and len( used_skip_sources )>=4 :
            if best_item:
                best_item["debug_note"] += u"－－规避医疗类问题{}".format("/".join(used_skip_sources))
            #母婴类，医疗类问题不能给出答案，要专业人士做这件事
            return None

        return best_item

    def search_baike_best(self,query, query_filter=2, query_parser=0, debug_item=None, keep_result=False):
        query_unicode = query
        if not isinstance(query, unicode):
            query_unicode = query.decode("utf-8")

        query_unicode = self.api_nlp.rewrite_zhidao_query(query_unicode)
        result = self.prepare_query(query_unicode, query_filter, query_parser, debug_item=debug_item)
        if not result:
            return False

        ret = result["ret"]
        result["query"] = query
        query_url = result["query_url"]
        if not self.api_nlp.is_question_baike( query_unicode , query_filter= query_filter, debug_item=debug_item):
            print "skip query, not baike", query_filter,  query_unicode
            return False

        ts_start = time.time()
        content = self.download(query_url)

        ret ["milliseconds_fetch"] = int( (time.time() - ts_start) * 1000 )

        if content:
            ts_start = time.time()
            search_result = parse_search_json_v0707(content)
            search_result_json = search_result["results"]
            ret ["total"] = search_result["total"]
            ret ["milliseconds_parse"] = int( (time.time() - ts_start) * 1000 )
            if keep_result or self.debug:
                ret["results"] = search_result_json

            best_item = self.select_best_qapair_0630(query_unicode, search_result_json)
            if best_item:
                ret ["best_qapair"] = best_item
                return ret
            #print json.dumps(search_result_json,ensure_ascii=False)

        #print ">>>>>>", content
        return ret

    def search_all(self, query, query_filter=0, query_parser=0, limit=10):
        max_page_number = (limit-1)/10+1
        output = { "items":[], "metadata":[], "query":query, "limit":limit,
                "query_filter":query_filter, "query_parser":query_parser }
        for page_number in range(max_page_number):
            result = self.prepare_query(query, query_filter, query_parser, use_skip_words=False)

            if not result:
                print query
                break

            ret = result["ret"]
            query_url = result["query_url"]
            query_unicode = ret["query"]

            ts_start = time.time()
            content = self.download(query_url)

            ret ["milliseconds_fetch"] = int( (time.time() - ts_start) * 1000 )

            if content:
                ts_start = time.time()
                search_result = parse_search_json_v0707(content)
                ret["milliseconds_parse"] = int( (time.time() - ts_start) * 1000 )
                output["items"].extend( search_result["results"] )
                output["metadata"].extend( ret )
                output["total"] = search_result["total"]

        return output

    def prepare_query(self, query, query_filter, query_parser, use_skip_words=True, page_number=0, debug_item=None):
        if not query:
            print "skip query, empty"
            if debug_item is not None:
                debug_item["debug_note"] = u"[-]问题空:prepare_query"
            return False

        query_unicode = query
        if not isinstance(query_unicode, unicode):
            query_unicode = query_unicode.decode("utf-8")

        if use_skip_words:
            detected_words = self.api_nlp.detect_skip_words(query_unicode)
            if detected_words:
                print "skip bad query, empty",  u"/".join( detected_words )
                if debug_item is not None:
                    debug_item["debug_note"] = u"[-]问题敏感词:{}".format( u"/".join( detected_words ) )
                return False

        query_unicode = re.sub(u"？$","",query_unicode)
        query_url, qword = self.get_search_url_qword(query_unicode, query_parser, page_number=page_number)

        ret = {
            "query":query_unicode,
        }

        if query_parser == 1:
            ret["qword"] = qword

        return {"ret":ret, "query_url":query_url}

    def search_chat_best(self,query, query_filter=2, query_parser=0):

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
            search_result = parse_search_json_v0707(content)
            search_result_json = search_result["results"]
            ret ["total"] = search_result["total"]
            ret ["milliseconds_parse"] = int( (time.time() - ts_start) * 1000 )

            #deprecated
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
                    encoding='gb18030',
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

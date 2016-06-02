#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# upgrade to qichacha2 2016-06-01 for its website revision, new batch_id qichacha2

from __future__ import print_function, division

from downloader import Downloader
from qiparser2 import QiParser

import lxml.html
import lxml.etree
import re
import json
import collections
import urllib

class Qichacha(object):

    def __init__(self, config, batch_id=None, groups=None,  refresh=False, request=True):
        if batch_id is None:
            batch_id = "qichacha0601"
        if config is None:
            raise Exception("error: missing config")

        self.config = config
        self.list_url = "http://www.qichacha.com/search?key={key}&index={index}&p={page}&province={province}"
        self.base_url = "http://www.qichacha.com/company_base?unique={key_num}&companyname={name}"
        self.invest_url = "http://www.qichacha.com/company_touzi?unique={key_num}&companyname={name}&p={page}"

        #self.VIP_MAX_PAGE_NUM = 500
        #self.MAX_PAGE_NUM = 10
        self.NUM_PER_PAGE = 10
        self.INDEX_LIST_PERSON = [4,6,14]
        self.INDEX_LIST_ORG = [2]
        self.PROVINCE_LIST = {
        "AH":[1,2,3,4,5,6,7,8,10,11,12,13,15,16,17,18,24,25,26,29],
        "BJ":[],
        "CQ":[],
        "FJ":[1,2,3,4,5,6,7,8,9,22],
        "GD":[1,2,3,4,5,6,7,8,9,12,13,14,15,16,17,18,19,20,51,52,53],
        "GS":[1,2,3,4,5,6,7,8,9,10,11,12,13,14,21,22,23,24,26,27],
        "GX":[],
        "GZ":[],
        "HAIN":[],
        "HB":[],
        "HEN":[],
        "HLJ":[],
        "HUB":[],
        "HUN":[],
        "JL":[],
        "JS":[],
        "JX":[],
        "LN":[],
        "NMG":[],
        "NX":[],
        "QH":[],
        "SAX":[],
        "SC":[],
        "SD":[],
        "SH":[],
        "SX":[],
        "TJ":[],
        "XJ":[],
        "XZ":[],
        "YN":[],
        "ZJ":[]}

        self.downloader = Downloader(config=config,
                                     request=request,
                                     batch_id=batch_id,
                                     groups=groups,
                                     refresh=refresh)
        self.downloader.login()
        self.parser = QiParser()



    # def list_person_search(self, person_list, limit=None, refresh=False):
    #     """.. :py:method::
    #         need to catch exception of download error
    #
    #     :param person_list: str or list type, search keyword
    #     :param limit: result number of every search keyword
    #     :rtype: {keyword1: {data: {name1: {}, name2: {}, ...}, metadata:{}},
    #               keyword2: {}, ...}
    #     """
    #     return self._list_keyword_search(person_list, self.INDEX_LIST_PERSON, limit, refresh )
    #
    # def list_corporate_search(self, corporate_list, limit=None, refresh=False):
    #     """.. :py:method::
    #         need to catch exception of download error
    #
    #     :param corporate_list: str or list type, search keyword
    #     :param limit: result number of every search keyword
    #     :rtype: {keyword1: {data: {name1: {}, name2: {}, ...}, metadata:{}},
    #               keyword2: {}, ...}
    #     """
    #     return self._list_keyword_search(corporate_list, self.INDEX_LIST_ORG, limit, refresh )

    def list_keyword_search(self, keyword_list, index_list, limit=None, refresh=False):
        if not isinstance(keyword_list, list):
            keyword_list = [keyword_list]

        if limit is None:
            max_page = self.config["MAX_PAGE_NUM"]
        else:
            max_page = (limit - 1) // self.NUM_PER_PAGE + 1
            max_page = min(self.config["MAX_PAGE_NUM"], max_page)

        result = {}
        for idx, keyword in enumerate(keyword_list):
            summary_dict = {}
            metadata_dict = collections.Counter()
            sum_e = 0
            sum_a = 0
            for index in index_list:

                index_expect = self.get_keyword_search_count(keyword, index, refresh)
                metadata_dict["expect"] += index_expect
                metadata_dict["i{}_e".format(index)] = index_expect
                #metadata_dict["total_[index:{}]_expect".format(index)]=cnt

                province_list = []
                summary_dict_by_index = {}
                if limit is None and index_expect>= self.config["MAX_PAGE_NUM"] * self.NUM_PER_PAGE:
                    print (" ---- expand [{}][index:{}] auto expand by province , expect {} ".format(keyword, index, index_expect) )
                    for province in self.PROVINCE_LIST:
                        self.list_keyword_search_onepass(keyword, index, province, max_page, metadata_dict, summary_dict_by_index, refresh)
                else:
                    self.list_keyword_search_onepass(keyword, index, "", max_page, metadata_dict, summary_dict_by_index, refresh)
                summary_dict.update(summary_dict_by_index)
                #metadata_dict["i{}_actual".format(index)]=len(summary_dict_by_index)
                i_sum_e =  metadata_dict["i{}_sum_e".format(index)]
                sum_e += i_sum_e
                sum_a += metadata_dict["i{}_sum_a".format(index)]
                if index_expect != i_sum_e:
                    print ( "[{}][index:{}] expect {} but sum_e is {}".format(keyword, index, index_expect, i_sum_e) )

            result[keyword] = {
                "data":summary_dict,
                "metadata":metadata_dict
            }
            metadata_dict["actual"] = len(summary_dict)
            if sum_e == sum_a:
                print (u" ---- ok [{}] {} ".format( keyword, json.dumps(metadata_dict, ensure_ascii=False, sort_keys=True) ))
            else:
                print (u"[{}] {} ".format( keyword, json.dumps(metadata_dict, ensure_ascii=False, sort_keys=True) ))

            #print ( json.dumps(summary_dict.keys(), ensure_ascii=False) )
        #print(json.dumps(result, ensure_ascii=False))
        return result

    def list_keyword_search_onepass(self, keyword, index, province, max_page, metadata_dict, summary_dict_onepass, refresh):
        summary_dict_local ={}
        cnt_expect = 0
        cnt_items = 0

        for page in range(1, max_page + 1):

            url = self.list_url.format(key=keyword, index=index, page=page, province=province)

            source = self.downloader.access_page_with_cache(url, groups="v0531,search,index{}".format(index), refresh=refresh)
            if not source:
                # no more results, cannot get data
                break

            tree = lxml.html.fromstring(source)

            if page ==1:
                cnt_expect = self.parser.parse_search_result_count(tree)
                metadata_dict["i{}_sum_e".format(index)]+=cnt_expect
                #metadata_dict["total_[index:{}]_expect2".format(index)]+=cnt
                #metadata_dict["total_[index:{}][省:{}]_expect2".format(index, province)]=cnt
                if cnt_expect >= self.config["MAX_PAGE_NUM"] * self.NUM_PER_PAGE:
                    msg = " ---- todo [{}][index:{}][省:{}] TO BE EXPAND , expect {}, ".format( keyword,index, province, cnt_expect)
                    print (msg)
                    metadata_dict["todo_expand"]+=1
                elif province:
                    #msg = "[{}][index:{}][省:{}], expect {}, ".format( keyword,index, province, cnt_expect)
                    #print (msg, end="")
                    pass

            if tree.cssselect("div.noresult .noface"):
                break

            items = self.parser.parse_search_result(tree)
            cnt_items += len(items)
            #print (page, len(temp), json.dumps(temp, ensure_ascii=False))
            for item in items:
                name = item['name']
                summary_dict_local[name]= item

            if len(items)<self.NUM_PER_PAGE:
                break

        #if province:
        metadata_dict["i{}_a_sum".format(index)]+= cnt_items
        cnt_actual = len(summary_dict_local)
        summary_dict_onepass.update( summary_dict_local )
        if cnt_expect==0 or cnt_actual==0 or abs(cnt_expect - cnt_actual)>0:
            url = self.list_url.format(key=keyword, index=index, page=0, province=province)
            msg = " ---- check [{}][{}], expect {} .....  {} items, {} actual".format( keyword, url, cnt_expect, cnt_items,  cnt_actual)
            print (msg)
            #print ( json.dumps(summary_dict_local.keys(), ensure_ascii=False) )

    def get_keyword_search_count(self, keyword, index, refresh=False):
        """.. :py:method::

        :param keyword: search keyword
        :rtype: count
        """
        url = self.list_url.format(key=keyword, index=index, page=1, province="")

        source = self.downloader.access_page_with_cache(url, groups="v0531,search,index{}".format(index),refresh=refresh)
        if not source:
            return 0

        #print (url, source)
        tree = lxml.html.fromstring(source)

        return  self.parser.parse_search_result_count(tree)


    def input_name_output_id(self, name):
        """.. :py:method::

        :param name: standard company name
        :rtype: qichacha id or None
        """
        url = self.list_url.format(key=name, index=0, page=1, province="")
        try:
            source = self.downloader.access_page_with_cache(url)
            tree = lxml.html.fromstring(source)
        except:
            source = self.downloader.access_page_with_cache(url)
            tree = lxml.html.fromstring(source)

        if tree.cssselect("div.noresult .noface"):
            return

        for i in tree.cssselect("#searchlist"):
            searched_name = i.cssselect(".name")[0].text_content().strip().encode("utf-8")
            if searched_name == name:
                link = i.cssselect(".list-group-item")[0].attrib["href"]
                return link.rstrip(".shtml").rsplit("_", 1)[-1]


    def _crawl_company_detail_by_name_id(self, name, key_num):
        """
        :rtype: {name: {"name": name,
                        "key_num", key_num,
                        "info": {},
                        "shareholders": {},
                       }
                }
        """
        url = self.base_url.format(name=name, key_num=key_num)
        try:
            source = self.downloader.access_page_with_cache(url)
            tree = lxml.html.fromstring(source)
        except:
            source = self.downloader.access_page_with_cache(url)
            tree = lxml.html.fromstring(source)

        all_info = self.parser.parse_detail(tree)
        all_info["info"]["name"] = name
        all_info.update({"name": name, "key_num": key_num})
        return {name: all_info}


    def crawl_company_detail(self, name, key_num=None, subcompany=True):
        """.. :py:method::

        :param name: standard company name
        :param key_num: qichacha company id,
                if don"t passed in this parameter,
                need to searching on website
        :param subcompany: whether to crawl subcompanies
        :rtype: json of this company info
        """
        if key_num is None:
            key_num = self.input_name_output_id(name)
            if key_num is None:
                return

        name_info_dict = self._crawl_company_detail_by_name_id(name, key_num)

        if subcompany is True:
            invest_info_dict = self.crawl_company_investment(name, key_num)
            if invest_info_dict is not None:
                name_info_dict[name]["invests"] = invest_info_dict[name].values()
        return name_info_dict


    def _crawl_company_investment_single_page(self, name, key_num, page, max_page_num=None):
        """.. :py:method::
            if parameter page is 1, parameter max_page_num must be []
        """
        if not hasattr(self, "_re_page_num"):
            setattr(self,
                    "_re_page_num",
                    re.compile("javascript:touzilist\((\d+)\)"))

        url = self.invest_url.format(key_num=key_num, name=name, page=page)
        try:
            source = self.downloader.access_page_with_cache(url)
            tree = lxml.html.fromstring(source)
        except:
            source = self.downloader.access_page_with_cache(url)
            tree = lxml.html.fromstring(source)

        if tree.cssselect("div.noresult .noface"):
            return

        if page == 1 and max_page_num == []:
            if tree.cssselect(".pagination #ajaxpage") == []:
                max_page_num.append(1)
            else:
                page_num = [ int( self._re_page_num.match( i.get("href") ).group(1) ) \
                    for i in tree.cssselect(".pagination #ajaxpage") ]
                page_num.append(1)
                max_page_num.append(max(page_num))

        return self.parser.parse_company_investment(tree)


    def crawl_company_investment(self, name, key_num):
        """.. :py:method::

        :param name: standard company name
        :param key_num: qichacha company id
        :rtype: {name: {sub_name1: {"name": sub_name1, "key_num": key_num},
                        sub_name2: {"name": sub_name2, "key_num": key_num}, ...}}
        """
        max_page_num = []
        invest_dict = self._crawl_company_investment_single_page(name,
                                                                 key_num,
                                                                 1,
                                                                 max_page_num)
        if invest_dict is None or invest_dict == {}:
            return
        if len(max_page_num) > 0:
            max_page_num = max_page_num[0]

        for page_idx in range(2, max_page_num + 1):
            invest_dict.update(self._crawl_company_investment_single_page(name,
                                                                     key_num,
                                                                     page_idx))
        return {name: invest_dict}


    def _parse_invests_inqueue(self,
                               name,
                               key_num,
                               already_crawled_names,
                               next_layer_name_id_set,
                               all_name_info_dict):

        name_info_dict = self.crawl_company_detail(name, key_num, subcompany=True)
        already_crawled_names.add(name)
        if "invests" in name_info_dict[name]:
            next_layer_name_id_set.update(
                [(i["name"], i["key_num"]) for i in name_info_dict[name]["invests"]\
                    if i["name"] not in already_crawled_names]
            )
        all_name_info_dict.update(name_info_dict)


    def crawl_descendant_company(self, name, key_num=None, limit=None):
        """.. :py:method::
            This company(detail, invests) is first layer, subcompanies(detail,
            invests) is second layer, ans so on.

        :param name: standard company name
        :param key_num: qichacha company id
        :param limit: limitation of descendants layers, None means unlimited
        """
        if key_num is None:
            key_num = self.input_name_output_id(name)
            if key_num is None:
                return
        if limit is None:
            limit = 2 ** 40

        already_crawled_names = set()
        all_name_info_dict = {}
        next_layer_name_id_set = set([(name, key_num)])

        while limit > 0 and next_layer_name_id_set:
            this_layer_name_id_set = next_layer_name_id_set
            next_layer_name_id_set = set()

            while this_layer_name_id_set:
                try:
                    sub_name, sub_key_num = this_layer_name_id_set.pop()
                    if sub_name in already_crawled_names:
                        continue

                    self._parse_invests_inqueue(sub_name,
                                                sub_key_num,
                                                already_crawled_names,
                                                next_layer_name_id_set,
                                                all_name_info_dict)
                except KeyError:
                    break
            limit -= 1

        return all_name_info_dict


    def _parse_shareholders_inqueue(self,
                                    name,
                                    key_num,
                                    already_crawled_names,
                                    next_layer_name_id_set,
                                    all_name_info_dict):

        name_info_dict = self.crawl_company_detail(name, key_num, subcompany=True)
        already_crawled_names.add(name)

        for shareholder in name_info_dict[name]["shareholders"]:
            if shareholder["link"] is not None:
                if shareholder["name"] not in already_crawled_names:
                    key_num = shareholder["link"].rstrip(".shtml").rsplit("_")[-1]
                    next_layer_name_id_set.add((shareholder["name"], key_num))
        all_name_info_dict.update(name_info_dict)


    def crawl_ancestors_company(self, name, key_num=None, limit=None):
        """.. :py:method::
            This company(detail, invests) is first layer, the shareholders(detail, invests)
            is second layer, shareholders of shareholders is third layer, and so on.

        :param name: standard company name
        :param key_num: qichacha company id
        :param limit: limitation of descendants layers, None means unlimited
        """
        if key_num is None:
            key_num = self.input_name_output_id(name)
            if key_num is None:
                return
        if limit is None:
            limit = 2 ** 40

        already_crawled_names = set()
        all_name_info_dict = {}
        next_layer_name_id_set = set([(name, key_num)])

        while limit > 0 and next_layer_name_id_set:
            this_layer_name_id_set = next_layer_name_id_set
            next_layer_name_id_set = set()

            while this_layer_name_id_set:
                try:
                    name, key_num = this_layer_name_id_set.pop()
                    if name in already_crawled_names:
                        continue

                    self._parse_shareholders_inqueue(name,
                                                     key_num,
                                                     already_crawled_names,
                                                     next_layer_name_id_set,
                                                     all_name_info_dict)
                except KeyError:
                    break
            limit -= 1
        return all_name_info_dict

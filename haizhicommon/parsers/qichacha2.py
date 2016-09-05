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

    def get_info_url(self, tab, key_num, name, page=None):
        if "NONAME" in name:
            name = "%20"
        if None == page or page == 1:
            ret = "http://www.qichacha.com/company_getinfos?unique={key_num}&companyname={name}&tab={tab}".format(key_num=key_num, name=name, tab=tab)
        else:
            ret = "http://www.qichacha.com/company_getinfos?unique={key_num}&companyname={name}&tab={tab}&page={page}".format(key_num=key_num, name=name, page=page, tab=tab)

        #if self.config.get('debug'):
        #    print (ret)

        return ret

    def __init__(self, config, batch_id=None, groups=None,  refresh=False, request=True, cache_only=False):
        if batch_id is None:
            batch_id = "qichacha0831"
        if config is None:
            raise Exception("error: missing config")

        self.config = config
        self.list_url = "http://www.qichacha.com/search?key={key}&index={index}&p={page}&province={province}"
        #self.base_url = "http://www.qichacha.com/company_getinfos?unique={key_num}&companyname={name}&tab=base"
        #self.invest_url = "http://www.qichacha.com/company_getinfos?unique={key_num}&companyname={name}&tab=touzi&p={page}"
        #self.legal_url = "http://www.qichacha.com/company_getinfos?unique={key_num}&companyname={name}&tab=susong&p={page}"

        #self.VIP_MAX_PAGE_NUM = 500
        #self.MAX_PAGE_NUM = 10
        #self.NUM_PER_PAGE = config.get('NUM_PER_PAGE',20 )  #10
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
                                     refresh=refresh,
                                     cache_only=cache_only)
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

    def list_keyword_search(self, keyword_list, index_list, limit=None, refresh=False, skip_index_max=None):
        """.. :py:method::
            对这样词语列表搜索结果的返回http://www.qichacha.com/search?key=%E5%8C%BB%E8%8D%AF&index=0

        :parameter keyword_list: 要搜索的词语列表
        :parameter index_list: 搜索条件的index编号列表
        :parameter limit: 搜索返回结果数限制，vip-5000，free-1000
        :rtype: hash, key is company, value is result json.
        """
        if not isinstance(keyword_list, list):
            keyword_list = [keyword_list]

        if limit is None:
            limit  =  self.config["MAX_LIMIT"]
        else:
            limit = min(limit, self.config["MAX_LIMIT"])

        result = {}
        for idx, keyword in enumerate(keyword_list):
            summary_dict = {}
            metadata_dict = collections.Counter()
            sum_e = 0
            sum_a = 0
            for index in index_list:
                result_info = self.get_keyword_search_result_info(keyword, index, refresh)
                index_expect = result_info["total"]

                #max_page = (limit - 1) // result_info["max_page_num"] + 1  #self.NUM_PER_PAGE + 1

                metadata_dict["expect"] += index_expect
                metadata_dict["i{}_e".format(index)] = index_expect
                #metadata_dict["total_[index:{}]_expect".format(index)]=cnt

                province_list = []
                summary_dict_by_index = {}
                if skip_index_max and index_expect >= skip_index_max:
                    print (" ---- undersample [{}][index:{}] 5000+ results".format(keyword, index))
                    self.list_keyword_search_onepass(keyword, index, "",  limit, metadata_dict, summary_dict_by_index, refresh)
                    pass
                elif limit is None and index_expect >= self.config["MAX_LIMIT"]:
                    print (" ---- expand [{}][index:{}] auto expand by province , expect {} ".format(keyword, index, index_expect) )
                    for province in self.PROVINCE_LIST:
                        self.list_keyword_search_onepass(keyword, index, province, limit, metadata_dict, summary_dict_by_index, refresh)
                elif index_expect > 0:
                    self.list_keyword_search_onepass(keyword, index, "",  limit, metadata_dict, summary_dict_by_index, refresh)
                else:
                    print (" ---- skip [{}][index:{}] no expected result".format(keyword, index))
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

    def list_keyword_search_onepass(self, keyword, index, province, limit, metadata_dict, summary_dict_onepass, refresh):
        """.. :py:method::
            对这样单个词搜索结果的返回http://www.qichacha.com/search?key=%E5%8C%BB%E8%8D%AF&index=0

        :parameter keyword: 要搜索的词语
        :parameter index: 搜索条件的index编号
        :parameter province: 搜索条件的省份（拼音开头字母?）
        :parameter limit: 搜索返回结果数限制，vip-5000，free-1000
        :rtype: hash, key is company, value is result json.
        """
        summary_dict_local ={}
        cnt_expect = 0
        cnt_items = 0

        for page in range(1, 1000):

            url = self.list_url.format(key=keyword, index=index, page=page, province=province)
            # print("into downloader")
            source = self.downloader.access_page_with_cache(url, groups="v0531,search,index{}".format(index), refresh=refresh)
            # print('downloader ended')
            if not source:
                # no more results, cannot get data
                break

            #if self.config.get("debug"):
            #    print (source)

            if "nodata.png" in source:
                # no more results, cannot get data
                break

            tree = lxml.html.fromstring(source)

            if page ==1:
                result_info = self.parser.parse_search_result_info(tree)
                cnt_expect = result_info["total"]
                metadata_dict["i{}_sum_e".format(index)] += cnt_expect
                metadata_dict["num_per_page"] = result_info["num_per_page"]

                #metadata_dict["total_[index:{}]_expect2".format(index)]+=cnt
                #metadata_dict["total_[index:{}][省:{}]_expect2".format(index, province)]=cnt
                if cnt_expect >= self.config["MAX_LIMIT"]:
                    msg = " ---- todo [{}][index:{}][省:{}] TO BE EXPAND , expect {}, ".format( keyword,index, province, cnt_expect)
                    print (msg)
                    metadata_dict["todo_expand"]+=1
                else:
                    if self.config.get("debug"):
                        msg = "---- regular [{}][index:{}][省:{}], expect {}, ".format( keyword,index, province, cnt_expect)
                        print (msg)

            if tree.cssselect("div.noresult .noface"):
                break

            items = self.parser.parse_search_result(tree)
            cnt_items += len(items)
            #print (page, len(temp), json.dumps(temp, ensure_ascii=False))
            for item in items:
                name = item['name']
                summary_dict_local[name]= item

            if cnt_items >= cnt_expect:
                break

            if cnt_items >= limit:
                break

            #if self.config.get("debug"):
            #    print (len(items), page)
            #if len(items)<self.NUM_PER_PAGE:
            #    break

        #if province:
        metadata_dict["i{}_sum_a".format(index)] += cnt_items
        cnt_actual = len(summary_dict_local)
        # print ('items: ', summary_dict_local)
        summary_dict_onepass.update( summary_dict_local )
        if cnt_expect==0 or cnt_actual==0 or abs(cnt_expect - cnt_actual)>0:
            url = self.list_url.format(key=keyword, index=index, page=0, province=province)
            msg = " ---- check [{}][{}], expect {} .....  {} items, {} actual".format( keyword, url, cnt_expect, cnt_items,  cnt_actual)
            print (msg)
            #print ( json.dumps(summary_dict_local.keys(), ensure_ascii=False) )

    def get_keyword_search_result_info(self, keyword, index, refresh=False):
        """.. :py:method::

        :param keyword: search keyword
        :rtype: json
        """
        url = self.list_url.format(key=keyword, index=index, page=1, province="")

        source = self.downloader.access_page_with_cache(url, groups="v0531,search,index{}".format(index),refresh=refresh)
        if not source:
            return 0

        #print (url, source)
        tree = lxml.html.fromstring(source)

        result_info = self.parser.parse_search_result_info(tree)
        result_info["keyword"] = keyword
        result_info["index"] = index
        return result_info


    def input_name_output_id(self, name):
        """.. :py:method::

        :param name: standard company name
        :rtype: qichacha id or None
        """
        url = self.list_url.format(key=name, index=0, page=1, province="")
        print(url)
        try:
            # print("into downloader")
            source = self.downloader.access_page_with_cache(url, refresh=True).replace('<em>', '').replace('</em>', '')
            tree = lxml.html.fromstring(source)
        except:
            source = self.downloader.access_page_with_cache(url)
            tree = lxml.html.fromstring(source)

        print('getting items')
        if tree.cssselect('.table-search-list') and tree.cssselect('.tp2_tit a'):
            items = tree.cssselect('.table-search-list')
            for i in items:
                #from lxml import etree as ET
                #print ("v3",  ET.tostring(i, pretty_print=True))
                if not i.xpath('.//*[@class=\"tp2_tit clear\"]/a/text()'):
                    continue
                item = {}
                item['name'] = i.xpath('.//*[@class=\"tp2_tit clear\"]/a/text()')[0]
                print(item['name'])
                item['href'] = i.xpath('.//*[@class=\"tp2_tit clear\"]/a/@href')[0]
                item['status'] = i.xpath('.//*[@class=\"tp5 text-center\"]/a/span/text()')[0]
                item['key_num'] = item['href'].split('firm_')[1].split('.shtml')[0]
                if item['name'] == name:
                    return item['key_num']
        # for i in tree.cssselect("#searchlist"):
        #     searched_name = i.cssselect(".name")[0].text_content().strip().encode("utf-8")
        #     if searched_name == name:
        #         link = i.cssselect(".list-group-item")[0].attrib["href"]
        #         return link.rstrip(".shtml").rsplit("_", 1)[-1]


    def _crawl_company_detail_by_name_id(self, name, key_num):
        """.. :py:method::
            给定company的name和key_num，获取该公司的详情内容，包括子公司

        :rtype: {name: {"name": name,
                        "key_num", key_num,
                        "info": {},
                        "shareholders": {},
                       }
                }
        """
        url = self.get_info_url("base", key_num, name)
        source = self.downloader.access_page_with_cache(url)
        if not source:
            print("no content")
            return {}
        try:
            tree = lxml.html.fromstring(source)
        except:
            if self.config.get("debug"):
                print (source)
            import traceback
            traceback.print_exc(file=sys.stdout)
            return {}

        all_info = self.parser.parse_detail(tree)
        print('all info:', json.dumps(all_info, ensure_ascii=False))
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
                print("no key_num")
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
                    re.compile("javascript:getTabList\((\d+)"))

        url = self.get_info_url("touzi",key_num, name, page=page)
        source = self.downloader.access_page_with_cache(url)
        if not source:
            return
        try:
            tree = lxml.html.fromstring(source)
        except:
            if self.config.get("debug"):
                print (source)
            import traceback
            traceback.print_exc(file=sys.stdout)
            return

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
            more_invest_dict = self._crawl_company_investment_single_page(name,
                                                                     key_num,
                                                                     page_idx)
            if more_invest_dict:
                invest_dict.update(more_invest_dict)

        return {name: invest_dict}


    def _parse_invests_inqueue(self,
                               name,
                               key_num,
                               already_crawled_names,
                               next_layer_name_id_set,
                               all_name_info_dict):

        name_info_dict = self.crawl_company_detail(name, key_num, subcompany=True)
        already_crawled_names.add(name)
        if "invests" in name_info_dict.get(name,{}):
            next_layer_name_id_set.update(
                [(i["name"], i["key_num"]) for i in name_info_dict[name]["invests"]\
                    if i["name"] not in already_crawled_names]
            )
        all_name_info_dict.update(name_info_dict)

    def crawl_company_expand(self, name, key_num=None, limit=None):
        """.. :py:method::
            爬取一个公司的子孙公司和父辈公司
        """
        if key_num is None:
            key_num = self.input_name_output_id(name)
            if key_num is None:
                return

        company_raw_one = {}
        temp = self.crawl_descendant_company(name, key_num, limit=limit)
        if temp:
            company_raw_one.update(temp)

        temp = self.crawl_ancestors_company(name, key_num, limit=limit)
        if temp:
            company_raw_one.update(temp)
        return company_raw_one


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

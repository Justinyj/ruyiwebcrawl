#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import requests
import time
import os
import sys
import json
import random
import collections

from headers import choice_agent, choice_proxy
from cache import Cache
from proxy import Proxy

class Downloader(object):
    """
        >>> list_url = 'http://qichacha.com/search?key={key}&index={index}&p={page}'
        >>> base_url = 'http://qichacha.com/company_base?unique={key_num}&companyname={name}'
        >>> invest_url = 'http://qichacha.com/company_touzi?unique={key_num}&companyname={name}&p={index}'

    """

    def __init__(self, config, request=False, batch_id='', groups=None, refresh=None, cache_only=False):
        self.request = request
        self.TIMEOUT = 10
        self.RETRY = 3
        self.cache_only = cache_only

        if batch_id == '':
            batch_id = os.path.dirname(__file__)
        self.cache = Cache(config, batch_id=batch_id)
        self.groups = groups
        self.config = config
        self.refresh = refresh
        self.counter = collections.Counter()

        self.cookie_index = 0
        self.cookies =[]
        worker_num = self.config.get('WORKER_NUM',1)
        worker_id = self.config.get('WORKER_ID',0)

        for idx, name in enumerate(sorted(list(self.config['COOKIES'].keys()))):
            if (idx % worker_num) != worker_id:
                #print ('skip cookies not for this worker', idx, idx % worker_num, name)
                continue

            v = self.config['COOKIES'][name]
            item = {
                'name': name,
                'value': v,
                'header': dict(i.split('=', 1) for i in v.split('; '))
            }
            self.cookies.append(item)

        #print (len(self.cookies))
        if worker_num  == 1:
            print ("cookies:", len(self.cookies),"gap:",self._get_sleep_period())
        else:
            print ("worker_id:",worker_id, " work_num:",worker_num, "; cookies:", len(self.cookies),"gap:",self._get_sleep_period())

        #exit(0)


    def login(self):

        if self.request is True:
            session = requests.Session()
            session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=3))
            session.headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate',
                'Accept-Language': 'zh-CN,en-US;q=0.7,en;q=0.3',
                'Cache-Control': 'max-age=0',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests' :'1',
                'Host': 'www.qichacha.com',
                'Connection': 'keep-alive',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.12; rv:49.0) Gecko/20100101 Firefox/49.0'
            }
            self.driver = session

        else:
            from selenium import webdriver
            self.driver = webdriver.Firefox()
            self.driver.get('https://graph.qq.com/oauth/show?which=Login&display=pc&response_type=code&client_id=101188807&redirect_uri=http%3A%2F%2Fwww.qichacha.com%2Fuser_callbackqq&state=8629a7fecfe3a1a81308915c97f38646&scope=get_user_info,add_share')
            self.driver.find_element_by_css_selector('#user_login .form-group [name=name]').send_keys('18623390999')
            self.driver.find_element_by_css_selector('#user_login .form-group [name=pswd]').send_keys('5201314pmm')
#            self.driver.find_element_by_css_selector('#user_login button[type=submit]').submit()
#            self.driver.find_element_by_css_selector('.col-sm-5 > a.btn-success').click()
            self.driver.implicitly_wait(30)
            time.sleep(15)

    def close(self):
        if self.request is False:
            self.driver.quit()

    def get_a_cookie(self):
        self.cookie_index = (self.cookie_index +1 ) % len(self.cookies)
        cookie = self.cookies[self.cookie_index]
        if self.config.get('debug'):
            print( "[debug] use cookie "+ cookie['name'] )
        return cookie

    def get_cur_cookie(self):
        return self.cookies[self.cookie_index]

    def pick_cookie_agent_proxy(self, url):
        self.driver.cookies.update( self.get_a_cookie()['header'] )
        #self.driver.headers['Cookie'] = self.get_a_cookie()['value']
        #self.driver.headers['Cookie'] = 'PHPSESSID=hd4pcd4a1hkdmtj7huc0akupr2; SERVERID=4ec4b3b70ba1eea2ca3e9ee7bf352bba|1464828343|1464828343; CNZZDATA1254842228=1066138900-1464827822-%7C1464827822'
        #self.driver.headers['Cookie'] = 'PHPSESSID=hd4pcd4a1hkdmtj7huc0akupr2; SERVERID=4ec4b3b70ba1eea2ca3e9ee7bf352bba|1464828343|1464828343; CNZZDATA1254842228=1066138900-1464827822-%7C1464827822'
        #print (self.driver.headers)
#        self.driver.headers['User-Agent'] = choice_agent()
#        proxies = choice_proxy(self.config, url)
#        self.driver.proxies.update(proxies)
#        return proxies

    def _get_sleep_period(self):
        sleep = self.config['CRAWL_GAP'] / len(self.cookies)

        #add a little bit random factor to crawler delay
        #sleep *= (1+random.random())
        #print (sleep)
        return sleep

    def request_download(self, url):
        ret = u''
        try:
            self.pick_cookie_agent_proxy(url)

            #print ("request_download", url)
            response = self.driver.get(url, timeout=self.TIMEOUT)
            if response.status_code == 200:
                ret = response.text  #unicode
        except:
            print ('failed', url, sys.exc_info()[0])
            pass
        finally:
            pass

        time.sleep(self._get_sleep_period()) # sleep of cookie

        return ret


    def selenium_download(self, url):
        for i in range(self.RETRY):
            try:
                self.driver.get(url)
                source = self.driver.page_source # unicode
                return source
            except:
                continue
            finally:
                time.sleep(self._get_sleep_period())
        else:
            return u''

    def check_content_invalid(self, content):
        if not content:
            return "invalid, empty"

        if len(content.strip()) ==0:
            return "invalid, empty"

        test_str = u"window.location.href"
        print (content)
        if test_str in content and content.index(test_str)<500:
            print (content)
            sys.exit(1)
            return "invalid,redirection"

#        if u"nodata.png" in content:
#            return "invalid, nodata"

    def access_page_with_cache(self, url, groups=None, refresh=None):

        def save_cache(url, content, groups, refresh):
            groups = self.groups if groups is None else groups
            self.counter["cache_write"]+=1
            ret = self.cache.post(url, content, groups, refresh)
            if ret not in [True, False]:
                print('save_cache failed',ret)

        refresh = self.refresh if refresh is None else refresh
        if not refresh:
            self.counter["cache_get"]+=1
            content = self.cache.get(url)
            #cache hit
            if content:
                self.counter["cache_hit"]+=1
                temp = self.check_content_invalid(content)
                if temp:
                    #print ("cache hit", url, temp)
                    pass
                else:
                    #print ("cache hit", url)
                    self.counter["cache_ok"]+=1
                    return content

        #print ("download", url)
        if self.cache_only:
            self.counter["cache_miss"]+=1
            return u''

        if self.request is True:
            self.counter["down_requests"]+=1
            content = self.request_download(url)
        else:
            self.counter["down_selenium"]+=1
            content = self.selenium_download(url)

        #print (content,"\n---------------", type(content))

        if not self.check_content_invalid(content):
            save_cache(url, content, groups, refresh)
            return content
        else:
            return u''

    def split_url(self, url):
        import urllib
        import re
        key, page = re.compile('http://www.qichacha.com/search?key=(.+)&index=0&p=(\d+)').match(url).groups()
        if key.startswith('%'):
            key = urllib.unquote(key)
        return key, page

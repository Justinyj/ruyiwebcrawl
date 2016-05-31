#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from selenium import webdriver
import requests
import time
import os
import sys
import json

from headers import choice_cookie, choice_agent, choice_proxy
from cache import Cache
from proxy import Proxy

class Downloader(object):
    """
        >>> list_url = 'http://qichacha.com/search?key={key}&index={index}&p={page}'
        >>> base_url = 'http://qichacha.com/company_base?unique={key_num}&companyname={name}'
        >>> invest_url = 'http://qichacha.com/company_touzi?unique={key_num}&companyname={name}&p={index}'

    """

    def __init__(self, config, request=False, batch_id='', groups=None, refresh=False):
        self.request = request
        self.TIMEOUT = 10
        self.RETRY = 3

        if batch_id == '':
            batch_id = os.path.dirname(__file__)
        self.cache = Cache(config, batch_id=batch_id)
        self.groups = groups
        self.config = config
        self.refresh = refresh


    def login(self):
        if self.request is True:
            session = requests.Session()
            session.mount('http://', requests.adapters.HTTPAdapter(pool_connections=30, pool_maxsize=30, max_retries=3))
            session.headers = {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh-CN,en-US;q=0.8,en;q=0.6',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.86 Safari/537.36',
                'Host': 'www.qichacha.com',
            }
            self.driver = session

        else:
            self.driver = webdriver.Firefox()
            self.driver.get('http://qichacha.com/user_login')
            self.driver.find_element_by_css_selector('#user_login .form-group [name=name]').send_keys('18623390999')
            self.driver.find_element_by_css_selector('#user_login .form-group [name=pswd]').send_keys('5201314pmm')
#            self.driver.find_element_by_css_selector('#user_login button[type=submit]').submit()
#            self.driver.find_element_by_css_selector('.col-sm-5 > a.btn-success').click()
            self.driver.implicitly_wait(30)
            time.sleep(15)

    def close(self):
        if self.request is False:
            self.driver.quit()


    def pick_cookie_agent_proxy(self, url):
        header_cookie = dict(i.split('=', 1) \
                for i in choice_cookie(self.config['COOKIES']).split('; '))
        #print (json.dumps(header_cookie))
        self.driver.cookies.update(header_cookie)
        self.driver.headers['User-Agent'] = choice_agent()
#        proxies = choice_proxy(self.config, url)
#        self.driver.proxies.update(proxies)
#        return proxies

    def _get_sleep_period(self):
        sleep = self.config['CRAWL_GAP'] / len(self.config['COOKIES'])
        #print (sleep)
        return sleep

    def request_download(self, url):
        for i in range(self.RETRY):
            proxies = self.pick_cookie_agent_proxy(url)

            try:
                #print(url)
                response = self.driver.get(url, timeout=self.TIMEOUT)
                #print (response.status_code, response.text)
                if response.status_code == 200:
                    return response.text #unicode
            except:
#                proxy = proxies.items()[0][1]
#                Proxy.instance().post(url, proxy)
                print ('failed', sys.exc_info()[0])
                pass
            finally:
                time.sleep(self._get_sleep_period()) # sleep of cookie
        else:
            return u''

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

    def access_page_with_cache(self, url, groups=None, refresh=None):

        def save_cache(url, source, groups, refresh):
            refresh = self.refresh if refresh is None else refresh
            groups = self.groups if groups is None else groups
            ret = self.cache.post(url, source, groups, refresh)
            if ret not in [True, False]:
                print(ret)

        content = self.cache.get(url)
        if content != u'':
            return content

        if self.request is True:
            source = self.request_download(url)
            if source == u'':
                return source
            save_cache(url, source, groups, refresh)

        else:
            source = self.selenium_download(url)
            if source == u'':
                return source
            save_cache(url, source, groups, refresh)

        return source


    def split_url(self, url):
        import urllib
        import re
        key, page = re.compile('http://qichacha.com/search?key=(.+)&index=0&p=(\d+)').match(url).groups()
        if key.startswith('%'):
            key = urllib.unquote(key)
        return key, page

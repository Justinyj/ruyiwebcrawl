#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cacheperiod import CachePeriod
import requests
import json


LOCAL = 'http://127.0.0.1:8000'
batch_id = 'chemppi'

def test_cache_post():

    url = "http://chem.100ppi.com/price/plist-357-1.html"
    content = requests.get(url).text

    data = json.dumps({ 'url': url, 'body': content})
    cache = CachePeriod(batch_id, LOCAL)

    post_ret = cache.post(url, data, refresh=True)

    print "post result: ", post_ret
    assert(post_ret == True)


def test_cache_get():

    url = "http://chem.100ppi.com/price/plist-357-1.html"
    new_cont = requests.get(url).text

    cache = CachePeriod(batch_id, LOCAL)
    content = json.loads(cache.get(url))
    
    assert(content['body'] == new_cont)

def test_cache_get_false():
    url = 'http://chem.100ppi.com'  # not cached url
    cache = CachePeriod(batch_id, LOCAL)
    content = cache.get(url)
    assert(content == '')


def main():
    test_cache_post()
    test_cache_get()
    test_cache_get_false()
    


if __name__ == '__main__':
    main()



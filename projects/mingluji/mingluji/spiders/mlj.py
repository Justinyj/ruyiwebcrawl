# -*- coding: utf-8 -*-
import scrapy
import re
import urllib
import json
from scrapy.spiders import Spider
from scrapy.spiders import Rule
from mingluji.items import Company
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class MinglujiSpider(Spider):
    name = "mingluji"
    allowed_domains = ["mingluji.com"]
    start_urls = (
        'http://mingluji.com/node/7',
    )

    def pass_item(self, i):
        return i

    def parse(self, response):
        url_by_province = response.xpath(
            '//td[@class="views-field views-field-field-province"]//@href')
        for url in url_by_province:
            yield scrapy.Request(url.extract(), callback=self.parse_for_city)

    def parse_for_city(self, response):
        url_by_city = response.xpath(
            '//div[@id="block-gongshang-mingluji-com-city"]//@href')
        for url in url_by_city:
            list_url = 'http://gongshang.mingluji.com/' + url.extract()
            yield scrapy.Request(list_url,
                                 callback=self.parse_for_industry,
                                 )

    def parse_for_industry(self, response):
        url_by_job = response.xpath(
            '//div[@id="block-gongshang-mingluji-com-industry"]//@href')
        for url in url_by_job:
            yield scrapy.Request(url.extract(),
                                 callback=self.parse_max_page,
                                 )

    def parse_max_page(self, response):
        try:
            max_content = response.xpath(
                '//li[@class="pager-last last"]//@href')[0].extract()
            max_num = int(max_content.rsplit('page=', 1)[1])
        except:
            max_num = 1
        for index in range(1, max_num + 1):
            url = response.url + '?page=' + str(index)
            yield scrapy.Request(url, callback=self.parse_single_page)

    def parse_single_page(self, response):
        titles = response.xpath(
            '//span[@class="views-field views-field-title"]//span[@class="field-content"]//text()')
        try:
            province = re.search('com/(.*?)/', response.url).group(1)
        except:
            province = 'failed'
        items = []
        for title in titles:
            item = Company()
            name = title.extract()
            item['name'] = name
            item['province'] = province
            items.append(item)
        for item in items:
            yield self.pass_item(item)  # much faster then yield in for
        return

# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider

from dongfangcaifu.items import Company  # url,title,content


class DongfangSpider(Spider):
    name = 'dongfang'
    allowed_domains = []
    start_urls = ['http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page=29218']

    def pass_item(self, i):
        return i

    def parse(self, response):
        # print response.encoding, 'coding'

        template = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page={}'
        for page in range(1, 35172):
            yield scrapy.Request(template.format(page), callback=self.parse2)
        return
        for url_tail in urls:
            break
            url = 'http://data.eastmoney.com' + url_tail.extract()
            yield scrapy.Request(url,
                                 headers={'Referer': 'https://www.baidu.com/'},
                                 callback=self.parse_notice)

    def parse2(self, response):
        pass

    def parse_notice(self, response):
        print response.url
        title = response.xpath('//div[@class="content"]/h4/text()').extract()
        if isinstance(title, list):
            title = title[0]
        item = Company()
        item['title'] = title
        item['url'] = response.url
        item['content'] = response.xpath(
            '//div[@class="content"]//pre/text()').extract()
        pass

# -*- coding: utf-8 -*-
import scrapy
from scrapy.spiders import Spider

from dongfangcaifu.items import Company  # url,title,content


class DongfangSpider(Spider):
    name = 'dongfang'
    allowed_domains = []
    start_urls = ['http://data.eastmoney.com/Notice']

    def pass_item(self, i):
        return i

    def parse(self, response):

        template = 'http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page={}'
        page_bottoms = response.xpath('//div[@class="Page"]//a')
        max_num = 1
        for node in page_bottoms:
            title = node.xpath('./@title').extract()
            if title:
                title = title[0]
            if title == u'转到最后一页':
                max_url = node.xpath('./@href').extract()[0]
                max_num = max_url[max_url.index('page=') + len('page=')::]
                max_num=int(max_num)
                break
        for page in range(1, 10):
            yield scrapy.Request(template.format(page), callback=self.parse_one_page)
        return

    def parse_one_page(self, response):
        # each page includes 50 notices
        urls = response.xpath('//td[@class="title"]/a/@href')
        for url_tail in urls:
            url = 'http://data.eastmoney.com' + url_tail.extract()
            print url
            break
            '''
            item=Company()
            item['url']=url
            yield self.pass_item(item) #generate url for each notice without parsing it
            continue
            '''
            yield scrapy.Request(url,
                                 callback=self.parse_notice)

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
        yield self.pass_item(item)

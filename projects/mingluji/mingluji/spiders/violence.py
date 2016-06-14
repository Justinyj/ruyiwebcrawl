# -*- coding: utf-8 -*-
import scrapy


class ViolenceSpider(scrapy.Spider):
    name = "violence"
    allowed_domains = ["mingluji.com"]
    start_urls = (
        'http://mingluji.com/',
    )
    

    def parse(self, response):
        pass

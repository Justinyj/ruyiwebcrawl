# -*- coding: utf-8 -*-
import scrapy
import urlparse
from yuer.items import Food
import json
import sys
import re
reload(sys)
sys.setdefaultencoding('utf-8')
class QuickSpider(scrapy.Spider):
    name = "quick"
    allowed_domains = []
    start_urls = (
        'http://www.mmbang.com',
    )

    def parse(self, response):
        header = {
        'Host': 'www.mmbang.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Cookie': '___rl__test__cookies=1468376738462; __fjswangyang=wy; sid=3054856846; skey=95278743; PHPSESSID=300ru3s3fgog93jpmbtn4e6hn4; last_vt=1468313939; referer=http%3A%2F%2Fwww.mmbang.com%2Fapp%2Fnbnc%2F117; OUTFOX_SEARCH_USER_ID_NCOO=1598010915.2667453; __utmt=1; uid=0; Hm_lvt_680ac5fedca30f7b2a9190575593f2eb=1468313939,1468315500; Hm_lpvt_680ac5fedca30f7b2a9190575593f2eb=1468377694; CNZZDATA30062626=cnzz_eid%3D2055464984-1468312897-http%253A%252F%252Fwww.mmbang.com%252F%26ntime%3D1468372297; __utma=105773727.111233205.1468313939.1468372074.1468375193.4; __utmb=105773727.30.10.1468375193; __utmc=105773727; __utmz=105773727.1468313939.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        }
        yield scrapy.Request(url='http://www.mmbang.com/app/nbnc', headers = header, callback = self.after_parse)


    def after_parse(self, response):
        header = {
        'Host': 'www.mmbang.com',
        'Connection': 'keep-alive',
        'Cache-Control': 'max-age=0',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
        'Cookie': '___rl__test__cookies=1468376738462; __fjswangyang=wy; sid=3054856846; skey=95278743; PHPSESSID=300ru3s3fgog93jpmbtn4e6hn4; last_vt=1468313939; referer=http%3A%2F%2Fwww.mmbang.com%2Fapp%2Fnbnc%2F117; OUTFOX_SEARCH_USER_ID_NCOO=1598010915.2667453; __utmt=1; uid=0; Hm_lvt_680ac5fedca30f7b2a9190575593f2eb=1468313939,1468315500; Hm_lpvt_680ac5fedca30f7b2a9190575593f2eb=1468377694; CNZZDATA30062626=cnzz_eid%3D2055464984-1468312897-http%253A%252F%252Fwww.mmbang.com%252F%26ntime%3D1468372297; __utma=105773727.111233205.1468313939.1468372074.1468375193.4; __utmb=105773727.30.10.1468375193; __utmc=105773727; __utmz=105773727.1468313939.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
        }
        food_node = response.xpath('//span[@class="nbnc_food_info"]/a/@href')
        for i in food_node:
            url = urlparse.urljoin('http://www.mmbang.com', i.extract())
            yield scrapy.Request(url = url,headers = header, callback = self.parse_per_food)
        #print response.body
        pass

    def parse_per_food(self, response):
        item = Food()
        name_node = response.xpath('//h1[@id = "home_title"]/text()')
        if len(name_node) > 0:
            item['name'] = name_node[0].extract().strip()
        else :
            return
        content_nodes = response.xpath('//div[contains(@class, "chapter_content nbnc_")]')
        
        pregnant_node = content_nodes[1]
        puerpera_node = content_nodes[2]
        baby_node = content_nodes[3]
        text = pregnant_node.xpath('.//text()').extract()
        
        if len(text) > 1 :
            pregnant = {
                'ok' : text[0].strip(),
                'reason' :text[1].strip(),
            }
        else :
            pregnant = {
                #'ok' : re.search('(.*?)(。|，|,|.)',text[0].strip()).group(1),
                'ok' : pregnant_node.xpath('./@class').extract()[0].replace("chapter_content nbnc_", ''),
                'reason' : ''.join(text),
            }

        text = puerpera_node.xpath('.//text()').extract()
        if len(text) > 1 :
            puerpera = {
                'ok' : text[0].strip(),
                'reason' :text[1].strip(),
            }
        else :
            puerpera = {
                'ok' : puerpera_node.xpath('./@class').extract()[0].replace("chapter_content nbnc_", ''),
                'reason' : ''.join(text),
            }

        text = baby_node.xpath('.//text()').extract()
        if len(text) > 1 :
            baby = {
                'ok' : text[0].strip(),
                'reason' :text[1].strip(),
            }
        else :
            baby = {
                'ok' : re.search('(.*?)(。|，|,|.)',text[0].strip()).group(1),
                'reason' : ''.join(text),
            }
        item['pregnant'] = pregnant
        item['puerpera'] = puerpera
        item['baby']  =baby
        f= open('eg.txt','a+')

        f.write(json.dumps(dict(item),ensure_ascii = False)+'\n')
        f.close()
        pass


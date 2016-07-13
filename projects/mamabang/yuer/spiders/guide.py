# -*- coding: utf-8 -*-
import scrapy
import json
import urlparse
from yuer.items import Advice
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class GuideSpider(scrapy.Spider):
    name = "guide"
    allowed_domains = []
    start_urls = (
        'http://www.mmbang.com/yuer',
    )

    def parse(self, response):
        header = {
            'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding':'gzip, deflate, sdch',
            'Accept-Language':'zh-CN,zh;q=0.8,en;q=0.6,zh-TW;q=0.4',
            'Cache-Control':'max-age=0',
            'Connection':'keep-alive',
            'Cookie':'__fjswangyang=wy; sid=3054856846; skey=95278743; PHPSESSID=300ru3s3fgog93jpmbtn4e6hn4; last_vt=1468313939; referer=http%3A%2F%2Fwww.mmbang.com%2Fapp%2Fnbnc%2F117; OUTFOX_SEARCH_USER_ID_NCOO=1598010915.2667453; __utmt=1; Hm_lvt_680ac5fedca30f7b2a9190575593f2eb=1468313939,1468315500; Hm_lpvt_680ac5fedca30f7b2a9190575593f2eb=1468395119; CNZZDATA30062626=cnzz_eid%3D2055464984-1468312897-http%253A%252F%252Fwww.mmbang.com%252F%26ntime%3D1468393897; uid=0; __utma=105773727.111233205.1468313939.1468386222.1468392984.7; __utmb=105773727.51.10.1468392984; __utmc=105773727; __utmz=105773727.1468313939.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)',
            'Host':'www.mmbang.com',
            'Upgrade-Insecure-Requests':'1',
            'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
        }

        for week in range(1,41):
            url = urlparse.urljoin('http://www.mmbang.com/yuer/', str(week))
            print url
            yield scrapy.Request(url = url, headers=header, callback=self.parse_per_page)
        
    #33 36 15 24 th week do not exist the guide
    def parse_per_page(self, response):
        item = Advice()
        item['week'] = response.url.replace('http://www.mmbang.com/yuer/','')
        nodes = response.xpath('//div[contains(@class, "section_")]')
        for index in range(len(nodes)):
            node = nodes[index]
            text = node.xpath('./li/text()').extract()
            if not text:
                continue
            if u'营养指导' in text[0]:
                break
        node = nodes[index+1]
        contents = node.xpath('.//text()').extract()
        item['content'] = ''.join(contents)
        item['content'] = item['content'].replace('\n','')
        f = open('guide.txt','a')
        f.write(json.dumps(dict(item), ensure_ascii = False))
        f.write('\n')
        f.close()







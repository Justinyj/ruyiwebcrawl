# -*- coding: utf-8 -*-
from cache import Cache
import scrapy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
BATCH_ID = 'dongfang-201606'


class MyMiddleWare(object):
    def process_request(self, request,  spider):
        url = request.url
        m = Cache(BATCH_ID)
        content = m.get(url)
        if content:
            response = scrapy.http.response.html.HtmlResponse(
                    url, encoding='utf-8', body=content)
            return response
        return

    def process_response(self, request, response, spider):
        url = response.url
        if response.status not in [200, 301]:
            f = open('log.txt', 'a')
            f.write(response.url+'\n')
            f.close()
            return responsex
        m = Cache(BATCH_ID)
        content = m.get(url)
        if not content:
            new_content = response.body 
            '''
            if '更多公告'  not  in new_content  :
                print 'no dataaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
                f=open('log.txt','a')
                f.write(url+'\n')
                f.close()
                return response
            '''
            m.post(url, new_content.decode('gb18030'))
            print 'I am pppppppppppppppposting to Cache'
        return response
'''
m=Cache(BATCH_ID)
print m.post('test','content3')
print m.get('http://data.eastmoney.com/Notice/Noticelist.aspx?type=0&market=all&date=&page=29718')
"""
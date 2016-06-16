# import requests
from cache import Cache
import scrapy
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
BATCH_ID = 'mingluji-201606'

m=Cache(BATCH_ID)
content=m.get('http://gongshang.mingluji.com/guizhou/')

class MyMiddleWare(object):

    def process_request(self, request,  spider):
        url=request.url
        m=Cache(BATCH_ID)
        content=m.get(url)
        if content:
        	response=scrapy.http.response.html.HtmlResponse(url,encoding='utf-8',body=content)
        	return response
        return


    def process_response(self, request, response, spider):
        url=response.url
        if response.status not in [200, 301]:
            f=open('log.txt','a')
            f.write(response.url)
            f.close()
            return response
        m=Cache(BATCH_ID)
        content=m.get(url)
        if not content:
        	new_content=response.body
        	m.post(url,new_content)
              #print 'I am pppppppppppppppposting to Cache'
        return response
'''
url='http://mingluji.com/'
m=Cache(BATCH_ID)
print m.get(url)
'''




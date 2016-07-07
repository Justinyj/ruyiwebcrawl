import scrapy
import sys

from downloader.downloader_wrapper import DownloadWrapper
reload(sys)
sys.setdefaultencoding('utf-8')
BATCH_ID = 'kuwo-20160706'
SERVER='http://192.168.1.179:8000/'
m = DownloadWrapper(SERVER)
f = open("/home/wl/lostpn.txt","a")

class MyMiddleWare(object):
    def process_request(self, request,  spider):
        url = request.url
        m = DownloadWrapper(SERVER)
        content = m.downloader_wrapper(url,BATCH_ID,0,encoding='utf-8')
        if content:
            response = scrapy.http.response.html.HtmlResponse(
                    url, encoding='utf-8', body=content)
            return response
        else:
            f.write(url)
            f.write('\n')
        return
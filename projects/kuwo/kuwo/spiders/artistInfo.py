import scrapy
import json
from kuwo.items import ArtistInfoItem
import codecs
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class art_spider(scrapy.Spider):
	name = "artist_info"
	start_urls = ["http://bd.kuwo.cn/mpage/api/artistList?pn=0&rn=1&bdfrom=haizhi&c=1m496rxeda48"]

	def parse(self, response):
		pn = response.meta.get('pn',0)
		result = json.loads(response.body.decode('utf-8','ignore')) 

		if not result:
			pn += 1
			nexturl = "http://bd.kuwo.cn/mpage/api/artistList?pn={}&rn=1&bdfrom=haizhi&c=1m496rxeda48".format(pn)
			yield scrapy.Request(nexturl, callback = self.parse, meta = {'pn':pn}, dont_filter = True)
			return
		
		if pn  > (int)(result['total']):
			return 

		pn += 1
		nexturl = "http://bd.kuwo.cn/mpage/api/artistList?pn={}&rn=1&bdfrom=haizhi&c=1m496rxeda48".format(pn)
		yield scrapy.Request(nexturl, callback = self.parse, meta = {'pn':pn}, dont_filter = True)

		for item in result["artistlist"]:
			iurl = "http://bd.kuwo.cn/mpage/api/artistInfo?artistid={}&bdfrom=haizhi&c=1m496rxeda48".format(item['id'])
			yield scrapy.Request(iurl, callback = self.parseArtistInfo, dont_filter = True)

	def parseArtistInfo(self, response):
		result = response.body

		if result:
			artistinfo = ArtistInfoItem()
			artistinfo['content'] = result
			yield artistinfo
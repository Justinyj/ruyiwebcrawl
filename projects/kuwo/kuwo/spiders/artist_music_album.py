#encoding:utf-8
'''根据歌手列表 爬取 每个歌手的 专辑 和 歌曲'''
import scrapy
import json
from kuwo.items import MusicItem, AlbumItem, ArtistItem, MusicInfoItem
import codecs
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class art_spider(scrapy.Spider):
	name = "artist_list"
	start_urls = ["http://bd.kuwo.cn/mpage/api/artistList?pn=0&rn=1&bdfrom=haizhi&c=1m496rxeda48"]

	def parseNext(response, rn, func, url, id):   #crawl the next page
		pn = response.meta.get('pn',0) + 1
		result = json.loads(response.body.decode('utf-8','ignore'))
		if id is None:
			nexturl = url.format(pn)
			nextmeta = {'pn':pn}
		else:
			nexturl = url.format(id, pn)
			nextmeta = {'pn':pn,'artistid':id}

		if not result or not 'total' in result:
			yield scrapy.Request(nexturl, callback = func, meta = nextmeta, dont_filter = True)
			return False

		if pn * rn > (int)(result['total']):
			return False

		yield scrapy.Request(nexturl, callback = func, meta = nextmeta, dont_filter = True)	
		return True


	def parse(self, response):  #for every artist, crawl it's music and album, and write aritst in file
		base_url = "http://bd.kuwo.cn/mpage/api/artistList?pn={}&rn=1&bdfrom=haizhi&c=1m496rxeda48"
		con = parseNext(response, 1, self.parse, base_url, None)

		if con == True:
			result = json.loads(response.body.decode('utf-8','ignore'))
			for item in result["artistlist"]:
				aurl = "http://bd.kuwo.cn/mpage/api/artistSongs?artistid={}&pn=0&rn=20&bdfrom=haizhi&c=1m496rxeda48".format(item['id'])
				yield scrapy.Request(aurl, callback = self.parseMusicByArtist, meta = {"artistid":item['id'], 'pn':0}, dont_filter = True)

				burl = "http://bd.kuwo.cn/mpage/api/artistalbum?artistid={}&pn=0&rn=20&bdfrom=haizhi&c=1m496rxeda48".format(item['id'])
				yield scrapy.Request(burl, callback = self.parseAlbum, meta = {"artistid":item['id'], 'pn':0}, dont_filter = True)

				artist = ArtistItem()
				artist['content'] = json.dumps(item,ensure_ascii=False)
				yield artist

	def parseMusicByArtist(self, response):
		base_url = "http://bd.kuwo.cn/mpage/api/artistSongs?artistid={}&pn={}&rn=20&bdfrom=haizhi&c=1m496rxeda48"
		con = parseNext(response, 20, self.parseMusicByArtist, base_url, response.meta['artistid'])

		if con == True:
			result = json.loads(response.body.decode('utf-8','ignore'))
			index_latest = 1
			for item in result["musiclist"]:
				item['id'] = item['musicrid']
				item['index_latest'] = index_latest
				index_latest +=1

				music = MusicItem()
				music['content'] = json.dumps(item,ensure_ascii=False)
				yield music		

				# murl = "http://bd.kuwo.cn/mpage/api/getMusicInfo?id={}&bdfrom=haizhi&c=1m496rxeda48".format(item['musicrid'])
				# yield scrapy.Request(murl, callback = self.parseMusicInfo, dont_filter = True)

	def parseAlbum(self, response):
		base_url = "http://bd.kuwo.cn/mpage/api/artistalbum?artistid={}&pn={}&rn=20&bdfrom=haizhi&c=1m496rxeda48"
		con == parseNext(response, 20, self.parseAlbum, base_url, response.meta['artistid'])

		if con == True:
			index_latest = 1
			for item in result["albumlist"]:
				item['id'] = item['albumid']
				item['index_latest'] = index_latest
				index_latest +=1

				album = AlbumItem()
				album['content'] = json.dumps(item,ensure_ascii=False)
				yield album

	def parseMusicInfo(self, response):
		result = response.body.decode('utf-8','ignore')

		if result:
			musicinfo = MusicInfoItem()
			musicinfo['content'] = result
			yield musicinfo


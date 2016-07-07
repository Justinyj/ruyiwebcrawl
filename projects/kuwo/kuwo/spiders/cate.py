import scrapy
import json
from kuwo.items import MusicCatItem, PlaylistItem
import codecs
import re

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

class cate_spider(scrapy.Spider):
    name = "cate_list"
    start_urls = ["http://bd.kuwo.cn/mpage/api/category?bdfrom=haizhi&c=1m496rxeda48"]
    
    def parse(self, response):
        result = json.loads(response.body.decode('utf-8','ignore'))
        
        for top1 in result['data']['list']:
            top1name = top1['name']
            for child2 in top1['children']:
                child2name = child2['name']

                tags = [u'{}:{}'.format(top1name,child2name),
                        u'C1C:{}'.format(top1name),
                        u'C2C:{}'.format(child2name)]

                pn = 0         
                turl = "http://bd.kuwo.cn/mpage/api/category?pn={}&rn=100&catId={}&bdfrom=haizhi&c=1m496rxeda48".format(pn,child2['catId'])                                                        
                yield scrapy.Request(url=turl, callback=self.parseCategoryList, meta={"tags": tags, 'pn':pn, 'catId':child2['catId']})                                   
                

    def parseCategoryList(self, response):
        result = json.loads(response.body.decode('utf-8','ignore'))
        if not result or not 'data' in result or not 'list' in result['data'] or len(result['data']['list']) == 0 :
        	return 

        tags = response.meta['tags']

        pn = response.meta['pn'] + 1
        catId = response.meta['catId']
        nexturl = "http://bd.kuwo.cn/mpage/api/category?pn={}&rn=100&catId={}&bdfrom=haizhi&c=1m496rxeda48".format(pn,catId)
        yield scrapy.Request(url = nexturl, callback = self.parseCategoryList, meta = {'tags':tags, 'pn':pn, 'catId':catId})

        for each in result['data']['list']:
            if 'catId' in each:
                ppn = 0
                turl = "http://nplserver.kuwo.cn/pl.svc?op=getlistinfo&encode=utf-8&keyset=pl2012&identity=kuwo&pn={}&rn=100&pid={}&bdfrom=haizhi&c=1m496rxeda48".format(ppn, each['catId'])
                yield scrapy.Request(turl, callback=self.parsePlaylist, meta={'tags':tags, 'ppn': ppn, 'catId':each['catId']}, dont_filter=True)


    def parsePlaylist(self, response):
    	result = json.loads(response.body.decode('utf-8','ignore'))
        if not 'musiclist' in result or len(result['musiclist']) == 0:
            return 

        ppn = response.meta['ppn']
        tags_cat = response.meta['tags']

        ppn = ppn + 1
        catId = response.meta['catId']
        nexturl = "http://nplserver.kuwo.cn/pl.svc?op=getlistinfo&encode=utf-8&keyset=pl2012&identity=kuwo&pn={}&rn=100&pid={}&bdfrom=haizhi&c=1m496rxeda48".format(ppn, catId)
        yield scrapy.Request(nexturl, callback = self.parsePlaylist, meta={'tags':tags_cat, 'ppn': ppn, 'catId':catId}, dont_filter=True)    	
    	
    	tags = []
        ppn = ppn - 1
    	tags.extend(tags_cat)
    	muscicatIt = MusicCatItem()
    	playlistIt = PlaylistItem()

        if ppn == 0:
            name = result.get('name')
            if name:
                tags.append(u'PN:{}'.format( name ))

            xtag = result.get('tag')
            xtag = re.sub(':[0-9]',"",xtag)
            #print xtag
            tags.extend( [u'PC:{}'.format(seg) for seg in xtag.split(',')] )

            playlist = {}
            playlist['id'] = catId
            for key in result:
                if key not in ["musiclist"]:
                    playlist[key] = result[key]

            playlist['tags'] = tags
            playlistIt['content'] = json.dumps(playlist,ensure_ascii=False)
            yield playlistIt

        for item in result['musiclist']:
            if 'musicid' in item:
                item['id'] = item['musicid']
            item['playlistid'] = catId
            item['tags'] = tags
            muscicatIt['content'] = json.dumps(item,ensure_ascii=False)
            yield muscicatIt

        
         

            








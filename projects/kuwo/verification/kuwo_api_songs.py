#encoding:utf-8
'''
统计api返回的每个歌手的数目，求和得出通过api能爬取到的歌曲数目总和
'''
import requests
import json
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


base_url = "http://bd.kuwo.cn/mpage/api/artistSongs?artistid={}&pn=0&rn=20&bdfrom=haizhi&c=1m496rxeda48" #歌手对应歌曲的api
fsongNum = open("./api_song_number.txt","w")   #统计每个歌手歌曲数目的文件

art_url = "http://bd.kuwo.cn/mpage/api/artistList?pn={}&rn=1&bdfrom=haizhi&c=1m496rxeda48"  #歌手列表的api
r_art = requests.get(art_url.format(0))
art_list = json.loads(r_art.content)
aritst_number = (int)(art_list['total'])  #总的歌手数目

sumSong = 0
print aritst_number

for pn in range(0, aritst_number):  #遍历页数，每页返回一个歌手（rn=1）,获得该歌手的id
	time.sleep(0.5)
	print pn, 

	list_url = art_url.format(pn)
	l = requests.get(list_url,timeout = 10)
	if l.status_code != 200 or l.url != list_url:
		fsongNum.write("failed to visit!\n")
	else:
		art = json.loads(l.content)
		aid = art['artistlist'][0]['id']
		print aid, 

		url = base_url.format(aid)   #根据该歌手的id获得其歌曲数目 
		r = requests.get(url, timeout=10)
		if r.status_code != 200 or r.url != url:
			fsongNum.write("failed to visit!\n")
		else:
			result = json.loads(r.content.decode('utf-8','ignore'))
			fsongNum.write(aid + " : ")
			fsongNum.write(str(result['total'])+'\n')
			print result['total']
			sumSong += (int)(result['total'])
	

fsongNum.write("total: " + str(sumSong))

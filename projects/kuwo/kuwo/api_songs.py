import requests
import json
import time

import sys
reload(sys)
sys.setdefaultencoding('utf-8')


base_url = "http://bd.kuwo.cn/mpage/api/artistSongs?artistid={}&pn=0&rn=20&bdfrom=haizhi&c=1m496rxeda48"
fsongNum = open("./api_song_number.txt","w")

url0 = "http://bd.kuwo.cn/mpage/api/artistList?pn={}&rn=1&bdfrom=haizhi&c=1m496rxeda48"
r0 = requests.get(url0.format(0))
result0 = json.loads(r0.content)
aritst_number = (int)(result0['total'])
sumSong = 0
print aritst_number

for pn in range(0, aritst_number):
	time.sleep(0.5)
	print pn, 

	list_url = url0.format(pn)
	l = requests.get(list_url,timeout = 10)
	if l.status_code != 200 or l.url != list_url:
		fsongNum.write("failed to visit!\n")
	else:
		art = json.loads(l.content)
		aid = art['artistlist'][0]['id']
		print aid, 

		url = base_url.format(aid)
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

#encoding:utf-8
'''
统计本地实际爬取的歌曲，包括：
每个歌手的歌曲数目（用于和api返回的每个歌手的数目对比）
重复的歌手数目
重复的歌曲数目
'''
import json
from collections import defaultdict

fsong = open("/home/wl/kuwoFile1/musicFile.json","r")
fartist = open("/home/wl/kuwoFile1/artistFile.json")
fdupa = open("./dup_artist.txt","w")   #dumplicate artist id
fdupm = open("./dup_music.txt","w")    #dumplicate music id
fsum = open("./localsongs.txt","w")    #song number of each artist actually crawled
total = 0

artists = {}
dup_artist = []
mmusic = {}
dup_music = []

#重复的歌手id
for line in fartist:
	art = json.loads(line)
	if artists.has_key(art['id']):
		dup_artist.append(art['id'])
	artists[art['id']] = 0

dup_artist.sort()

for d in dup_artist:
	fdupa.write(d + '\n')

#重复的歌曲,及每个歌手的歌曲数目
for line in fsong:
	music = json.loads(line)
	artists[music['artistid']] += 1

	if mmusic.has_key(line):
		dup_music.append(music['musicrid'] + "__" + music['artistid'])
	mmusic[line] = 0

# dup_music.sort()
for d in dup_music:
	fdupm.write(d + '\n')

s = sorted(artists.iteritems(),key = lambda x:x[0])

for each in s:
	fsum.write(each[0] + "  " + str(each[1]) + '\n')
	total += each[1]

fsum.write("total: " + str(total))

'''
重复出现一次的歌手数目 4000左右

重复写了一次的歌曲数目 16万左右 去重后剩余250万左右歌曲
'''

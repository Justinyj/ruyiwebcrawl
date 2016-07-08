import json
from collections import defaultdict

fsong = open("/home/wl/kuwoFile1/musicFile1.json","r")
fartist = open("/home/wl/kuwoFile1/artistFile.json")
fdupa = open("./dup_artist.txt","w")   #dumplicate artist id
fdupm = open("./dup_music.txt","w")    #dumplicate music id
fsum = open("./localsongs.txt","w")    #song number of each artist actually crawled
total = 0

artists = {}
dup_artist = []
mmusic = {}
dup_music = []

for line in fartist:
	art = json.loads(line)
	if artists.has_key(art['id']):
		dup_artist.append(art['id'])
	artists[art['id']] = 0

dup_artist.sort()

for d in dup_artist:
	fdupa.write(d + '\n')


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

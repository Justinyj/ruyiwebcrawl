import json
import re

f=open('mingluji_urls.txt','r')
count={}
total=0
while(1):
	line=f.readline().strip()
	try:
	    item=json.loads(line)
	except:
	    break
	provin=re.search('com/(.*?)/',item['url']).group(1)
	a=count.get(provin)
	if not a:
		count[provin]=item['num']
		total+=item['num']
	else:
		count[provin]+=item['num']
		total+=item['num']
	#count[provin]+=item[num]
f.close()
print count
print total

f=open('0','r')
content=f.read()
f.close()
# -*- coding: utf-8 -*-
import json
import re

file_name = 'mingluji_urls.txt'
f = open(file_name, 'r')
with open('out.txt', 'w') as out:
    while(1):
        line = f.readline()
        if line:
            line = line.strip()
            print line
            item=json.loads(line)
            max_url,num=item['url'],item['num']
            index=max_url.find('=')

            for postion in range(num+1):
                url=max_url[0:index]+'={}'.format(postion)
                out.write(url+'\n')

        else:
            break
f.close()

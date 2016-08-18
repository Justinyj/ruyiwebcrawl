# -*- coding: utf-8 -*-
import os
import json
import csv
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')

path = os.path.abspath(os.curdir)

def parse_file(filename):
    with open(filename, 'r') as f:
        for line in f:
	    if not line.strip():
		continue
            item = json.loads(line.strip())
            with open('company_names', 'a') as out:
                out.write(item['manufacturer_chs'] + '\n')
file_list = os.listdir(path)
for filename in file_list:
    print filename
    if 'get' in filename:
	continue
    parse_file(filename)

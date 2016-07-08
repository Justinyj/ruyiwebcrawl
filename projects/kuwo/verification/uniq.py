#encoding:utf-8
#去除文件中的重复行
from __future__ import print_function

import sys
reload(sys)
sys.setdefaultencoding('utf-8')

import collections

def process(filename):
    d = collections.defaultdict(int)
    with open(filename, 'r') as f:
        for line in f.readlines():
            d[line.decode('utf-8')] += 1
    with open(filename + '.new', 'w') as f:
        for key, _ in d.items():
            f.write(key)

if __name__ == '__main__':
    assert len(sys.argv) == 2
    process(sys.argv[1])
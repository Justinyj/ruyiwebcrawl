#coding=utf-8
import nose
import libdata
import json
import libnlp
import sys
import csv
def run_skip_words(text):
    lib = libnlp.SimpleNlp()
    skip_words = lib.detect_skip_words(text)
    if (skip_words):
        print 'skip'+text
    #print "test_skip_words: {} | text: {} | skip:".format( len(skip_words)>0, text), json.dumps(skip_words, ensure_ascii=False)

def is_ban(line):
    ban_list = ['爱情','想你','婚姻','造句','zaojv','我爱你','夫妻','抑郁','痛苦','感情','玫瑰','沉默','拥抱','爱你','死亡','坟墓','沉沦','暴力','性感','性爱']
    for ban in ban_list:
        if ban in line:
            return True
    return False

with open('out2.xls', 'r') as f:
    lib = libnlp.SimpleNlp()
    for line in f:
        line = line.strip()
        skip_words = lib.detect_skip_words(line)
        if skip_words:
            print line
            continue
        if is_ban(line):
            print line
            continue
        line = line.replace('""','')
        if not line:
            continue
        with open('out3.xls','a') as f3:
            spamwriter = csv.writer(f3, quoting=csv.QUOTE_MINIMAL)

            spamwriter.writerow([line])
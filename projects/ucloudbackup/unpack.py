# -*- coding:utf-8 -*-
from pymongo import MongoClient
import os
import subprocess
import requests
import pymongo
import json
import datetime


from_path = '/data/baidu_dir/back/{}/{}'
to_path   = '/data/monitor/check'
output_name = 'ucloud_mongon_udb_backup_{}.tgz'.format(datetime.datetime.now().strftime('%Y%m%d'))


def get_real_path():
    now = datetime.datetime.now()
    day_of_month = now.day
    if day_of_month % 15 == 0:
        return from_path.format("monthly", output_name)

    day_of_week = now.weekday()
    if day_of_week % 7 == 0:
        return from_path.format("weekly", output_name)

    return from_path.format("daily", output_name)

def unpack():
    real_path = get_real_path()
    os.system('tar zxvf {} -C {}'.format(real_path, to_path))
    print "finished"

#os.system('rm -rf /data/monitor/check/tmp')




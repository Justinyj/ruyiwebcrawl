#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 程序目的是从ucloud得到其每天更新的备份文件，按照一定的规则转存本地并抛弃旧备份。 
# 每次下载备份时需要发送一个http request，成功后在response里则会得到备份文件的下载地址。此请求主要需要的是备份ID与DBId，后者是个常量。
# 另外api的每次请求都要在URL里附上电子签名，其值由所有其他的参数与private_key共同确定后，还要再加到url里。
# 对于云端而言，可得到的备份ID有多个，每天运行程序取其创建日期最新的进行下载。
# 对于本地文件，当daily中的备份超过七个，则保留最新七个。weekly中的备份超过四个，则保留最新四个。（本程序采取先删到六个和三个再下载新备份的逻辑。）
# 备份的分类：每月15日的备份放入monthly文件夹中，每周一的备份放入weekly文件夹中，每天的备份放入daily文件夹中，发生冲突时优先级依次降低。
# 注意：各个参数计算签名时不用url转码，而当其拼接起来生成最终url时需要转码。

'''
crontab config:
# m h  dom mon dow   command
* 4 * * * /usr/bin/python2.7 /data/baidu_dir/back/backup.py
'''
from secret import PUBLIC_KEY, PRIVATE_KEY

import requests
import hashlib
import urlparse
import urllib
import datetime
import json
import os
import re
HOME = '/data/baidu_dir/back'

class UcloudApiClient(object):
    '''
    To get the Backup Downloading Adress shoul pass these parameters: (Region, DBId = 'udb-sbjftb', BackupId)
    Get BackupId through DescribeUDBBackup API.(Also could get DBId through Another API.)

    '''

    def __init__(self, public_key, private_key, region='cn-bj2', DBId='udb-sbjftb'):
        self.public_key = public_key
        self.private_key = private_key
        self.domain = 'http://api.ucloud.cn/?'
        self.region = region
        self.DBId = DBId
        self.BackupId = ''

    def get_signature(self, params):
        items = params.items()
        items.sort()
        params_data = ""
        for key, value in items:
            params_data = params_data + str(key) + str(value)
        params_data = params_data + self.private_key
        sign = hashlib.sha1()
        sign.update(params_data)
        signature = sign.hexdigest()
        return signature

    def get_newest_backup_id(self):
        params = {
            'Action'    :  'DescribeUDBBackup',
            'Region'    :  self.region,
            'Offset'    :  0,
            'Limit'     :  30,  # Usually the totalcount of backups is about 15.
            'PublicKey' :  self.public_key,
        }
        signature = self.get_signature(params)
        url = self.domain + urllib.urlencode(params) + '&Signature={}'.format(signature)
        req = requests.get(url)

        try:
            Backups = req.json()['DataSet']
        except:
            return

        Backups.sort(lambda x, y: cmp(x[u'BackupTime'], y[u'BackupTime']), reverse=True)
        for item in Backups:
            # There are 2 kinds of DBId : udb-sbjftb and udb-4oe3nq
            if item[u'DBId'] == self.DBId:
                newest_backup = item
                break
        else:
            return

        newest_backup_id = newest_backup['BackupId']
        return newest_backup_id

    def get_newest_backup_url(self):
        self.BackupId = self.get_newest_backup_id()
        if not self.BackupId:
            print 'Failed in getting BackupId'
            return

        params = {
            'Action'    :  'DescribeUDBInstanceBackupURL',
            'Region'    :  self.region,
            'DBId'      :  self.DBId,
            'BackupId'  :  self.BackupId,
            'PublicKey' :  self.public_key
        }
        signature = self.get_signature(params)
        url = self.domain + urllib.urlencode(params) + '&Signature={}'.format(signature)
        req = requests.get(url)

        res_item = req.json()
        if res_item[u'RetCode'] is not 0:
            print 'Get download URL failed!'
            return
        backup_path = res_item[u'BackupPath']
        return backup_path


def download_newest_backup(folder):
    client = UcloudApiClient(PUBLIC_KEY, PRIVATE_KEY)
    for _ in range(0, 3):  
        backup_path = client.get_newest_backup_url().strip() 
        if backup_path:
            break 
    else:
        return

    output_name = 'ucloud_mongon_udb_backup_{}.tgz'.format(datetime.datetime.now().strftime('%Y%m%d'))
    os.system(('wget -c  "{}" -O "{}/{}/{}"').format(backup_path, HOME, folder, output_name))


def check_folders():
    """
    Also OK with './daily',  absolute path might be safer?
    """
    #home = os.path.abspath('.')
    path = os.path.join(HOME , 'daily')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(HOME , 'weekly')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(HOME , 'monthly')
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    check_folders()

    now = datetime.datetime.now()
    day_of_month = now.day
    if day_of_month == 15:
        download_newest_backup('monthly')
        return

    #home = os.path.abspath('.')
    day_of_week = now.weekday()
    if day_of_week % 7 == 0:
        week_files = os.listdir(HOME + '/weekly')
        if len(week_files) >= 4:
            sorted_files = sorted(week_files, key=lambda filename: os.stat(os.path.join(HOME, 'weekly', filename)).st_ctime)
            for i in range(0, len(week_files)-3):
                os.remove(os.path.join(HOME, 'weekly', sorted_files[i]))
        download_newest_backup('weekly')
        return 
    
    day_files = os.listdir(HOME + '/daily')
    if len(day_files) >= 7:
        sorted_files = sorted(day_files, key=lambda filename: os.stat(os.path.join(HOME, 'daily', filename)).st_ctime)
        for i in range(0,len(day_files)-6):
            os.remove(os.path.join(HOME, 'daily', sorted_files[i]))
    
    download_newest_backup('daily')

if __name__ == '__main__':
    main()




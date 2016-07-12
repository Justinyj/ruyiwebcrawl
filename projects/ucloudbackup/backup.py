#!/usr/bin/env python
# -*- coding: utf-8 -*-

from secret import PUBLIC_KEY, PRIVATE_KEY

import requests
import hashlib
import urlparse
import urllib
import datetime
import json
import os
import re


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

    output_name = '{}.tgz'.format(datetime.datetime.now().strftime('%Y%m%d'))
    os.system(('wget -c  "{}" -O "./{}/{}"').format(backup_path, folder, output_name))


def check_folders():
    """
    Also OK with './daily',  absolute path might be safer?
    """
    home = os.path.abspath('.')
    path = os.path.join(home + '/daily')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(home + '/weekly')
    if not os.path.exists(path):
        os.makedirs(path)
    path = os.path.join(home + '/monthly')
    if not os.path.exists(path):
        os.makedirs(path)

def main():
    check_folders()

    now = datetime.datetime.now()
    day_of_month = now.day
    if day_of_month % 15 == 0:
        download_newest_backup('monthly')
        return

    home = os.path.abspath('.')
    day_of_week = now.weekday()
    if day_of_week % 7 == 0:
        week_files = os.listdir(home + '/weekly')
        if len(week_files) >=4:
            sorted_files = sorted(week_files, key=lambda filename: os.stat(os.path.join(home, 'weekly', filename)).st_ctime)
            for i in range(0, len(week_files)-3):
                os.remove(os.path.join(home, 'weekly', sorted_files[i]))
        download_newest_backup('weekly')
        return 
    
    day_files = os.listdir(home + '/daily')
    if len(day_files) >= 7:
        sorted_files = sorted(day_files, key=lambda filename: os.stat(os.path.join(home, 'daily', filename)).st_ctime)
        for i in range(0,len(day_files)-6):
            os.remove(os.path.join(home, 'daily', sorted_files[i]))
    
    download_newest_backup('daily')

if __name__ == '__main__':
    main()







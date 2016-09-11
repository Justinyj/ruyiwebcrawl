# !/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

import os
import paramiko
import time
import datetime
import pytz
import hashlib

# 由于daily文件夹里的文件数量在几百个到一千个左右，所以下面get_newest_create_time()中的时间开销并不会太大。

class DataMover(object):
    def __init__(self, ipaddr = '52.198.100.109', username='admin', batch_id='kmzydaily'):
        self.batch_id = batch_id
        self.ipaddr = ipaddr
        self.username = username
        self.ssh = paramiko.SSHClient()
        self.ssh.load_system_host_keys()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh.connect(ipaddr, username=username)

    def get_dir_name(self, batch_id):
        now = datetime.datetime.utcnow().date()
        suffix = str(now).replace('-', '')
        dir_name = '{}-{}'.format(batch_id, suffix)
        self.dir_path = os.path.join('/data/hproject/2016', dir_name)
        return dir_name

    def check_dailydir_exist(self):                     # 当日的数据文件夹格式为：kmzydaily-20160909
        stdin, stdout, stderr = self.ssh.exec_command('ls /data/hproject/2016/')  # 所有爬虫数据都储存在此路径下
        dir_name = self.get_dir_name(self.batch_id)
        dir_list = stdout.read().strip().split('\n')
        return dir_name in dir_list

    def get_newest_create_time(self):
        stdin, stdout, stderr = self.ssh.exec_command("cd {}; ls -l --time=ctime".format(self.dir_path))
        rows = stdout.read().strip().split('\n')[1:]        # 第一行是total 描述，去掉

        newest_creat_time = None 
        for row in rows:                                    # row的格式: -rw-r--r-- 1 admin admin 4401 Sep  8 07:14 ff22a80c953068db08581e783b6b69b4e5e588ad
            row = row.replace('  ', ' ')                    # Sep和8之间有两个空格
            date_string = '-'.join(row.split(' ')[5:8])     #  Sep-9-06:29
            date_string = '2016-' + date_string
            creat_time =  datetime.datetime.strptime(date_string, '%Y-%b-%d-%H:%M')
            if not newest_creat_time:
                newest_creat_time = creat_time
            newest_creat_time = max(newest_creat_time, creat_time)      # todo: 加一个对newest_creat_time为None的判断？

        return newest_creat_time

    def wait_for_finished(self):
        # 检查逻辑：当文件夹中最新的文件创建时间距今30分钟以上，则判断为爬虫已跑完
        # todo: 排除卡死在循环里的情况
        while  1:                       
            print 'waiting'
            now = datetime.datetime.utcnow()
            newest_time = self.get_newest_create_time()
            delta = now - newest_time
            if delta.seconds > 1800:
                break                     # 另一种粗暴的方法：hour*60 + minute  - now.hour*60 - now.minute > 30 
            time.sleep(60)

    def move_data(self):
        # todo :处理异常情况（MD5不相同）
        # 由于两台机上的数据储存目录结构相同，所以本地和远程用的都是dir_path，无需变换
        print('moving')
        self.ssh.exec_command('tar cvzf {}.tar.gz -C {} .'.format(self.dir_path, self.dir_path))
        os.system('scp {}@{}:{}.tar.gz {}.tar.gz'.format(self.username, self.ipaddr, self.dir_path, self.dir_path))
        stdin, stdout, stderr = self.ssh.exec_command("md5sum {}.tar.gz".format(self.dir_path))

        md5_remote = stdout.read().split(' ')[0]
        md5_local = ''
        with open('{}.tar.gz'.format(self.dir_path), 'r') as f:   
            md5_local = hashlib.md5(f.read()).hexdigest()
        self.ssh.exec_command('rm {}.tar.gz'.format(self.dir_path))

        if md5_remote == md5_local:
            os.system('mkdir {} -p;tar zxvf {}.tar.gz -C {}'.format(self.dir_path, self.dir_path, self.dir_path))
            os.system('rm {}.tar.gz'.format(self.dir_path))
            return True
        else:
            return False
        
    def run(self):
        if self.check_dailydir_exist():
            print 'exist: ' + self.dir_path
            self.wait_for_finished()
            self.move_data()
            return True
        else:
            print 'no such directory' + self.dir_path     # 不存在此文件夹，说明爬虫方面异常
            #slack('Warning: Can not find the data directory\n batch_id :{}'.format(self.batch_id))
            return False


if __name__ == '__main__':
    eg = DataMover()
    eg.run()

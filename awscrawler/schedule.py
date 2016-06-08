#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division
from math import ceil

import time
import paramiko

from ec2manager import Ec2Manager

class Schedule(object):

    def __init__(self, machine_num, tag, cycle=600, *args, **kwargs):
        self.machine_num = machine_num
        self.cycle = cycle
        self.group_num = int(ceil(machine_num * 2 / cycle)) if machine_num * 2 >= cycle else 1
        self.restart_interval = 0 if machine_num * 2 >= cycle else cycle / machine_num 

        self.ec2manager = Ec2Manager(tag)
        self.ids = self.ec2manager.create_instances(self.machine_num)
        self.id_cookie_dict = self._assign_cookies(kwargs.get('cookies', []))

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def _assign_cookies(self, cookies):
        id_cookie_dict = {}
        if len(cookies) == 0:
            pass
        elif len(cookies) == 1:
            id_cookie_dict = {i:cookies[0] for i in self.ids}
        elif len(self.ids) % len(cookies) == 0:
            quotient = len(self.ids) // len(cookies)
            begin = 0
            for i in range(len(cookies)):
                id_cookie_dict.update( {j:cookies[i] for j in self.ids[begin:begin+quotient]} )
                begin += quotient
        else:
            print('length of machine is not divisible by length of cookies')
        return id_cookie_dict


    def run(self, *args, **kwargs):
        time.sleep(30)

        before = time.time()
        while 1:
            ids = self.ec2manager.stop_and_start(self.group_num)
            for i in ids:
                idx = self.ec2manager.get_idx_by_id(i)
                base_cmd = ('/home/admin/.virtualenvs/crawlerservice/bin/python'
                            ' /opt/service/awscrawler/worker.py -i {}'
                            ' '.format(idx))
                if i in self.id_cookie_dict:
                    command = base_cmd + "-c '{}'".format(self.id_cookie_dict[i])
                else:
                    command = base_cmd
                ipaddr = self.ec2manager.get_ipaddr(i)
                self.remote_command(ipaddr, command)

            if self.restart_interval != 0:
                now = time.time()
                sleep_interval = before + self.restart_interval - now
                if sleep_interval > 0:
                    time.sleep(sleep_interval)
                before = now


    def remote_command(self, ipaddr, command):
        try:
            self.ssh.connect(ipaddr, username='admin')
            ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(command)
        finally:
            self.ssh.close()


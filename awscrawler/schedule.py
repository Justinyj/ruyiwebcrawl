#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import time
import paramiko

from math import ceil
from paramiko.ssh_exception import NoValidConnectionsError

from settings import REGION_NAME, ENV
from awsapi.ec2manager import Ec2Manager

class Schedule(object):

    def __init__(self, machine_num, tag, cycle=1200, backoff_timeout=10, *args, **kwargs):
        self.machine_num = machine_num
        self.cycle = cycle
        self.group_num = int(ceil(machine_num * 2 / cycle)) if machine_num * 2 >= cycle else 1
        self.restart_interval = 0 if machine_num * 2 >= cycle else cycle / machine_num

        self.backoff_timeout = 30 * backoff_timeout / 2**3 # magic number because queue.get

        self.ec2manager = Ec2Manager(REGION_NAME, tag)
        self.ids = self.ec2manager.create_instances(self.machine_num)
        self.id_cookie_dict = self._assign_cookies(kwargs.get('cookies', []))

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        keypair = self.ec2manager.get_keypair()
        self.pkey = paramiko.RSAKey.from_private_key_file('/home/admin/.ssh/{}.pem'.format(keypair))
        paramiko.util.log_to_file('awscrawler_paramiko.log')

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


    def run_command(self, one_id, base_cmd):
        print(base_cmd)
        idx = self.ec2manager.get_idx_by_id(one_id)
        if one_id in self.id_cookie_dict:
            command = base_cmd.format(idx) + ' -c "{}"'.format(self.id_cookie_dict[one_id])
        else:
            command = base_cmd.format(idx)
        print(command)
        ipaddr = self.ec2manager.get_ipaddr(one_id)
        self.remote_command(ipaddr, command)


    def run_forever(self, *args, **kwargs):
        base_cmd = ('cd /opt/service/awscrawler; source env.sh {env}; '
                    'dtach -n /tmp/worker.sock python worker.py -i {{}}'
                    ' -t {timeout}'.format(env=ENV, timeout=self.backoff_timeout))

        for i in self.ids:
            self.run_command(i, base_cmd)

        while 1:
            before = time.time()
            ids = self.ec2manager.stop_and_start(self.group_num)
            for i in ids:
                self.run_command(i, base_cmd)

            if self.restart_interval != 0:
                now = time.time()
                sleep_interval = before + self.restart_interval - now
                if sleep_interval > 0:
                    time.sleep(sleep_interval)
                before = now


    def remote_command(self, ipaddr, command, repeat=20):
        for _ in range(repeat):
            try:
                self.ssh.connect(ipaddr, username='admin', pkey=self.pkey)
                ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(command)
                break
            except NoValidConnectionsError:
                time.sleep(10)
            except:
                time.sleep(10)
        self.ssh.close()


    def stop_all_instances(self, *_):
        self.ec2manager.terminate(self.ids)

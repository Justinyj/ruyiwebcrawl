#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import os
import time
import paramiko

from awsapi.ec2manager import Ec2Manager

class Controller(object):
    def __init__(self, batch_id, machine_num, region_name='ap-northeast-1'):
        self.batch_id = batch_id
        self.batch_key = batch_id.rsplit('-', 1)[0]
        self.machine_num = machine_num

        self.ec2manager = Ec2Manager(region_name, tag)

        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        keypair = self.ec2manager.get_keypair()
        self.pkey = paramiko.RSAKey.from_private_key_file('/home/admin/.ssh/{}.pem'.format(keypair))

        self.id_cookie_dict = {}


    def start_instances(self):
        self.ids = self.ec2manager.create_instances(self.machine_num)
        length = min(len(self.ids), 30)
        time.sleep(length)


    def run_command(self, one_id, base_cmd):
        idx = self.ec2manager.get_idx_by_id(one_id)
        if one_id in self.id_cookie_dict:
            command = base_cmd.format(idx) + '-c "{}"'.format(self.id_cookie_dict[one_id])
        else:
            command = base_cmd.format(idx)
        ipaddr = self.ec2manager.get_ipaddr(one_id)
        self.remote_command(ipaddr, command)


    def remote_command(self, ipaddr, command, repeat=11):
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


    def run(self, fname):
        import marshal
        import zlib
        import base64

        with open(fname) as fd:
            content = fd.read()
        cmd = base64.b64encode(zlib.compress( marshal.dumps(compile(content, '', 'exec')), 9 ))
        base_cmd = 'cd /home/admin/reducer; source env.sh;  python reducer.py -i {{}} -m {total} -p {cmd}'.format(total=self.machine_num, cmd=cmd)

        for i in self.ids:
            self.run_command(i, base_cmd)


    @classmethod
    def dryrun(cls, fname, total):
        import marshal
        import zlib
        import base64

        with open(fname) as fd:
            content = fd.read()
        cmd = base64.b64encode(zlib.compress( marshal.dumps(compile(content, '', 'exec')), 9 ))
        base_cmd = 'python reducer.py -i 3 -m {total} -p {cmd}'.format(total=total, cmd=cmd)
        print(base_cmd)
        os.system(base_cmd)



def parse_arg():
    import argparse
    parser = argparse.ArgumentParser(prog='python controller.py',
                                     description='server that control distributed client.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--batch_id', '-b', type=str, help='batch_id')
    parser.add_argument('--machine_num', '-m', type=str, help='number of all machines')
    parser.add_argument('--program', '-p', type=str, help='file to transmit to client for executing')
    parser.add_argument('--region_name', '-r', type=str, default='ap-northeast-1', help='region of s3')
    parser.add_argument('--dryrun', '-d', type=bool, help='not start instance, for local debug')
    return parser.parse_args(), parser


def main():
    args, parser = parse_arg()

    try:
        if not args.program:
            raise()
        if args.dryrun:
            Controller.dryrun(args.program, 10)
        else:
            app = Controller(args.batch_id, args.machine_num, args.region_name)
            app.start_instances()
            app.run(args.program)

    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(e)
        parser.print_help()


if __name__ == '__main__':
    main()


# encoding=utf-8
import glob
import os
import sys
import json
import collections
import codecs
import re
import hashlib
import datetime
import logging
from secret import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import boto3
import paramiko
import subprocess
import time

gcounter = collections.Counter()


class InstanceMgr:
    def __init__(self):
        self.CRAWLER_TAG_KEY='crawler'
        self.CRAWLER_TAG_VALUE='qichacha'
        self.FILENAME_PEM="/Users/lidingpku/.ssh/crawl-tokyo.pem"

        self.conn = boto3.resource('ec2',
            region_name='ap-northeast-1',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    def create(self, crawler_num):
        instances = self.conn.create_instances(DryRun=False,
            ImageId='ami-7bbe501a',
            MinCount=crawler_num,
            MaxCount=crawler_num,
            KeyName='crawl-tokyo',
            InstanceType='t2.micro',
            SecurityGroupIds=['launch-wizard-1'])

        print "create", len(list(instances))
        for instance in instances:
            self.conn.create_tags(
                Resources=[instance.id],
                Tags=[
                    {
                        'Key': self.CRAWLER_TAG_KEY,
                        'Value': self.CRAWLER_TAG_VALUE,
                    }])



    def select(self, state=None):
        filters = [
            {
               'Name': 'tag:'+self.CRAWLER_TAG_KEY,
               'Values': [ self.CRAWLER_TAG_VALUE ]
           }
        ]

        if state:
            filters.append(
                {
                    'Name': 'instance-state-name',
                    'Values': [state]
                }
            )

        return self.conn.instances.filter(Filters=filters)

    def stop(self):
        instances = self.select('running')
        print "stop", len(list(instances))
        instances.stop()

    def start(self, worker_num=None):
        instances = self.select('stopped')
        i_num = len(list(instances))
        print "start", worker_num, "out of ", i_num
        if worker_num is None:
            instances.start()
        else:
            if i_num < worker_num:
                print "not enough workers", i_num, worker_num
            for idx, instance in enumerate(instances):
                if idx< worker_num:
                    instance.start()


    def list(self):
        instances = self.select()
        print "list", len(list(instances))
        for i in instances:
            print i.id, i.instance_type, i.public_ip_address, i.state['Name']

    def clear(self):
        instances = self.select()
        print "terminate", len(list(instances))
        instances.terminate()

    def _execute_cmd(self, host, user, cmds):
        k = paramiko.RSAKey.from_private_key_file(self.FILENAME_PEM)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print "Connecting to {}@{}".format(user, host)
        ssh.connect(host, username = user, pkey = k)
        for command in cmds:
            print "Executing {}".format(command)
            stdin , stdout, stderr = ssh.exec_command(command)
            #print stdout.read()
            #print stderr.read()
        ssh.close()
        print 'closed'

    def run(self, worker_num, cmds):
        instances = self.select('running')
        i_num = len(list(instances))
        if worker_num != i_num:
            print "mismatch running:{}, expect worker:{} ".format(i_num, worker_num)
            return

        print "run",i_num
        for idx, i in enumerate(instances):
            self._execute_cmd(i.public_ip_address,'ubuntu', cmds)
            print "# ssh ubuntu@{} -i {}".format(i.public_ip_address, self.FILENAME_PEM),

    def upload(self, worker_num):
        instances = self.select('running')
        i_num = len(list(instances))
        if worker_num != i_num:
            print "mismatch running:{}, expect worker:{} ".format(i_num, worker_num)
            return

        print "upload", i_num
        for i in instances:
            cmds = [
                "# ssh ubuntu@{} -i {}".format(i.public_ip_address, self.FILENAME_PEM),
                "/usr/bin/rsync -azvrtopg -e '/usr/bin/ssh -o StrictHostKeyChecking=no -i {}' /Users/lidingpku/haizhi/project/ruyiwebcrawl/projects/qichacha  ubuntu@{}:/data/ruyi/ruyiwebcrawl/projects".format(self.FILENAME_PEM, i.public_ip_address)
                #"ping {}".format( i.public_ip_address)
            ]
            for cmd in cmds:
                print "{}".format(cmd)
                ret = subprocess.call(cmd, shell=True)
                print ret



def main():
    #print sys.argv

    if len(sys.argv)<2:
        print 'help'
        return

    option= sys.argv[1]

    mgr = InstanceMgr()
    if "create" == option:
        new_worker_num= sys.argv[2]
        mgr.create(int(new_worker_num))
    elif "list" == option:
        mgr.list()
    elif "stop" == option:
        mgr.stop()
    elif "start" == option:
        if len(sys.argv)>2:
            work_num = int(sys.argv[2])
        else:
            work_num = None
        mgr.start(work_num)

    elif "run_prefetch" == option:
        cmds = [
            "python -u /data/ruyi/ruyiwebcrawl/projects/qichacha/business/crawljob.py fetch medical {} > out.prefetch.{} &".format(idx, datetime.datetime.now().isoformat())
        ]
        mgr.run(15,cmds)
    elif "run_fetch" == option:
        cmds = [
            "python -u /data/ruyi/ruyiwebcrawl/projects/qichacha/business/crawljob.py fetch medical > out.fetch{} &".format(datetime.datetime.now().isoformat())
        ]
        mgr.run(1,cmds)
    elif "upload" == option:
        if len(sys.argv)>2:
            work_num = int(sys.argv[2])
        else:
            work_num = 15
        mgr.upload(work_num)


if __name__ == "__main__":
    main()
    gcounter[datetime.datetime.now().isoformat()]=1
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

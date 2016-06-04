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

    def start(self):
        instances = self.select('stopped')
        print "start", len(list(instances))
        instances.start()

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

    def run(self, worker_num):
        instances = self.select('running')
        if worker_num!=len(list(instances)):
            print "not enough running worker ", len(list(instances))
            return

        print "run", len(list(instances))
        for idx, instance in enumerate(instances):
            cmds = [
                "python -u /data/ruyi/ruyiwebcrawl/projects/qichacha/business/crawljob.py fetch medical {} > out.{} &".format(idx, datetime.datetime.now().isoformat())
            ]
            self._execute_cmd(instance.public_ip_address,'ubuntu', cmds)

    def upload(self, worker_num):
        instances = self.select('running')
        if worker_num!=len(list(instances)):
            print "not enough running worker ", len(list(instances))
            return

        print "upload", len(list(instances))
        for i in instances:
            cmds = [
                "# ssh ubuntu@{} -i {}".format(i.public_ip_address, self.FILENAME_PEM),
                "/usr/bin/rsync -azvrtopg -e '/usr/bin/ssh -i {}' /Users/lidingpku/haizhi/project/ruyiwebcrawl/projects/qichacha  ubuntu@{}:/data/ruyi/ruyiwebcrawl/projects".format(self.FILENAME_PEM, i.public_ip_address)
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
        mgr.start()
    elif "run" == option:
        mgr.run(18)
    elif "upload" == option:
        mgr.upload(18)


if __name__ == "__main__":
    main()
    gcounter[datetime.datetime.now().isoformat()]=1
    print json.dumps(gcounter,ensure_ascii=False,indent=4, sort_keys=True)

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
import boto3
import paramiko
import subprocess
import time
import json

class InstanceMgr:
    def __init__(self, config):
        self.config = config
        self.conn = boto3.resource('ec2',
            region_name= config['region_name'],
            aws_access_key_id=config["aws_access_key_id"],
            aws_secret_access_key=config["aws_secret_access_key"])

    def create(self, job_index, worker_num):
        job_config = self.config["jobs"][job_index]
        instances = self.conn.create_instances(DryRun=False,
            ImageId=job_config["ImageId"],
            MinCount=worker_num,
            MaxCount=worker_num,
            KeyName=job_config["KeyName"],
            InstanceType=job_config["InstanceType"],
            SecurityGroupIds=job_config["SecurityGroupIds"])

        print "create", len(list(instances))


    def select(self, job_index, state=None):
        filters = [
            { 'Name':'image-id','Values':[self.config["jobs"][job_index]["ImageId"]] }
        ]

        if state:
            filters.append(
                {'Name': 'instance-state-name','Values': [state]}
            )

        return self.conn.instances.filter(Filters=filters)

    def stop(self, job_index):
        instances = self.select(job_index, 'running')
        print "stop", len(list(instances))
        instances.stop()

    def start(self, job_index, worker_num=None):
        instances = self.select(job_index, 'stopped')
        i_num = len(list(instances))
        print "start", worker_num, "out of ", i_num
        if worker_num is None:
            instances.start()
        else:
            if i_num < worker_num:
                print "SKIP, not enough workers", i_num, worker_num
                return
            for idx, instance in enumerate(instances):
                if idx < worker_num:
                    instance.start()

    def list(self, job_index):
        job_config = self.config["jobs"][job_index]
        instances = self.select(job_index)
        counter = collections.Counter()
        print "list", job_config["note"], len(list(instances))
        for i in instances:
            print i.id, i.instance_type, i.public_ip_address, i.state['Name']
            counter["state_"+i.state['Name']]+=1
            counter["type_"+i.instance_type]+=1
            self.print_ssh(job_index, i)
        print json.dumps(counter,ensure_ascii=False,indent=4, sort_keys=True)

    def print_ssh(self, job_index, i):
        job_config = self.config["jobs"][job_index]
        if i.public_ip_address:
            print "ssh {}@{}\n".format(job_config["username"], i.public_ip_address)

    def terminate(self, job_index):
        instances = self.select(job_index)
        print "terminate", len(list(instances))
        instances.terminate()

    def _execute_cmd(self, host, username, cmds, filename_pem):
        k = paramiko.RSAKey.from_private_key_file(filename_pem)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print "\nConnecting to {}@{}".format(username, host)
        ssh.connect(host, username = username, pkey = k)
        for command in cmds:
            print "Executing {}".format(command)
            stdin , stdout, stderr = ssh.exec_command(command)
            print stdout.read()
            print stderr.read()
        ssh.close()
        print 'closed'

    def run(self, job_index, worker_num, cmds_option, filename_pem):
        job_config = self.config["jobs"][job_index]
        instances = self.select(job_index, 'running')
        i_num = len(list(instances))
        if worker_num != i_num:
            print "SKIP mismatch running:{}, expect worker:{} ".format(i_num, worker_num)
            return
        cmds=self.config["cmds"]
        print "run",i_num, cmds_option
        for idx, i in enumerate(instances):
            print "========="
            cmds_selected = []
            for cmd in cmds[cmds_option]:
                temp = cmd.format(worker_id=idx, worker_num=worker_num, timestamp=datetime.datetime.now().isoformat())
                cmds_selected.append(temp)
            self._execute_cmd(i.public_ip_address, job_config["username"], cmds_selected, filename_pem)
            self.print_ssh(job_index, i)


    def upload(self, job_index, worker_num):
        instances = self.select(job_index, 'running')
        i_num = len(list(instances))
        if worker_num != i_num:
            print "SKIP mismatch running:{}, expect worker:{} ".format(i_num, worker_num)
            return

        print "upload", i_num
        for i in instances:
            cmds = [
#                "/usr/bin/rsync -azvrtopg -e '/usr/bin/ssh -o StrictHostKeyChecking=no ' /Users/lidingpku/haizhi/project/ruyiwebcrawl/local/qichacha/business/server  ubuntu@{}:/data/ruyi/ruyiwebcrawl/local/qichacha/business".format(i.public_ip_address),
                "/usr/bin/rsync -azvrtopg -e '/usr/bin/ssh -o StrictHostKeyChecking=no ' /Users/lidingpku/haizhi/project/ruyiwebcrawl/local/qichacha/business/work  ubuntu@{}:/data/ruyi/ruyiwebcrawl/local/qichacha/business".format(i.public_ip_address),
                "/usr/bin/rsync -azvrtopg -e '/usr/bin/ssh -o StrictHostKeyChecking=no ' /Users/lidingpku/haizhi/project/ruyiwebcrawl/projects/qichacha  ubuntu@{}:/data/ruyi/ruyiwebcrawl/projects".format(i.public_ip_address),
                #"ping {}".format( i.public_ip_address)
            ]
            print "\n==================\n"
            for cmd in cmds:
                print "{}".format(cmd)
                ret = subprocess.call(cmd, shell=True)
                print ret
                print ""
                print "ssh ubuntu@{} -i {}".format(i.public_ip_address)
                print ""



def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def main(config):
    #print sys.argv

    if len(sys.argv)<3:
        print 'help'
        print 'python api_aws.py qichacha_0612 list'
        return

    job_index= sys.argv[1]
    option= sys.argv[2]


    mgr = InstanceMgr(config)
    if "create" == option:
        worker_num= sys.argv[3]
        mgr.create(job_index, int(worker_num))
    elif "list" == option:
        mgr.list(job_index)
    elif "stop" == option:
        mgr.stop(job_index)
    elif "terminate" == option:
        mgr.terminate(job_index)
    elif "start" == option:
        if len(sys.argv)>3:
            work_num = int(sys.argv[3])
        else:
            work_num = None
        mgr.start(job_index, work_num)

    elif "upload" == option:
        if len(sys.argv)>3:
            work_num = int(sys.argv[3])
        else:
            work_num = THE_WORKER_NUM
        mgr.upload(job_index, work_num)

    elif "run" == option:
        if len(sys.argv)>5:
            worker_num = int(sys.argv[3])
            cmds_option = sys.argv[4]
            filename_pem = sys.argv[5]
            mgr.run(job_index, worker_num, cmds_option, filename_pem)
        else:
            print "SKIP , not enough params"

if __name__ == "__main__":
    filename = getTheFile("local/config_aws.json")
    print filename
    with open(filename) as f:
        config = json.load(f)
    main(config)

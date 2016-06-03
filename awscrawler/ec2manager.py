#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import boto3
from collections import deque

from secret import EC2_ACCESS_ID, EC2_SECRET_KEY

REGION_NAME = 'ap-northeast-1'
AMI_ID = 'ami-d7d4c5b9'
KEYPAIR = 'kg-proxy-tokyo'
INSTANCE_TYPE = 't2.micro'
SECURITYGROUPID = 'sg-fcbf0998'

class Ec2Manager(object):

    def __init__(self):
        self.ec2 = boto3.resource('ec2', region_name=REGION_NAME, aws_access_key_id=EC2_ACCESS_ID, aws_secret_access_key=EC2_SECRET_KEY)

    def create_instances(self,
                         MachineNum=1,
                         ImageId=AMI_ID,
                         KeyName=KEYPAIR,
                         InstanceType=INSTANCE_TYPE,
                         SecurityGroupIds=[SECURITYGROUPID]):
        """ ec2.Instance(id='i-336303ac')
        """
        self.ins = self.ec2.create_instances(ImageId=ImageId,
                                             MinCount=MachineNum,
                                             MaxCount=MachineNum,
                                             KeyName=KeyName,
                                             InstanceType=InstanceType,
                                             SecurityGroupIds=SecurityGroupIds)
        self.queue = deque(self.ins)


    def start(self, ids):
        self.ec2.instances.filter(InstanceIds=ids).start()

    def stop(self, ids):
        self.ec2.instances.filter(InstanceIds=ids).stop()

    def terminate(self, ids):
        self.ec2.instances.filter(InstanceIds=ids).terminate()

    def get_ids_in_status(self, status):
        """
        :param status: pending, running, stopping,, stopped, shutting-down
        """
        instances = self.ec2.instances.filter(
                Filters=[{'Name': 'instance-state-name', 'Values': [status]}])
        return [i.id for i in instances]

    def stop_one_and_restart(self):
        instance = self.queue.popleft()

        self.stop([instance.id])
        while 1:
            instance.load() # load cost network time
            if instance.meta.data[u'State'][u'Name'] == 'stopped':
                break

        self.start([instance.id])
        while 1:
            instance.load()
            if instance.meta.data[u'State'][u'Name'] == 'running':
                break

        self.queue.append(instance)


    def stop_and_start(self, group_num):
        group_instances = []
        ids = []
        for _ in xrange(group_num):
            item = self.queue.popleft()
            group_instances.append(item)
            ids.append(item.id)

        self.stop(ids)
        while 1:
            count = []
            for i in group_instances:
                i.load()
                count.append(1 if i.meta.data[u'State'][u'Name'] == 'stoped' else 0)
            if sum(count) == len(ids):
                break

        self.start(ids)
        while 1:
            count = []
            for i in group_instances:
                i.load()
                count.append(1 if i.meta.data[u'State'][u'Name'] == 'running' else 0)
            if sum(count) == len(ids):
                break

        self.queue.extend(group_instances)

import time
import boto3
import re
import logging
import traceback

AWS_ACCESS_KEY_ID = 'AKIAIFM563SKK5KM6F5A'
AWS_SECRET_ACCESS_KEY = 'BMOgdoiwN4q+Mio7csBe4riZ7DPqUx0gIQrtrhYZ+Y8/Y59ttsp'
sg_names = 'worker'  # sg-048eab63 launch-wizard-1
REGION_NAME = 'ap-northeast-1'
INSTANCE_TYPE = 't2.micro'
IMA_ID = "IMA"


class EC2manager(object):

    def get_connected(self, ):
        self.conn = boto3.resource('ec2', region_name='ap-northeast-1', aws_access_key_id='AKIAIFM563SKK5KM6F5A',
                                   aws_secret_access_key='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')

    def __init__(self):
        self.conn = None
        self.instances = None
        self.ids = []

    def create_instances(self, ImageId='ami-d7d4c5b9', MinCount=1, MaxCount=1, KeyName='kg-proxy-tokyo', InstanceType='t2.micro'):
        ins = self.conn.create_instances(
            ImageId=ImageId, MinCount=MinCount, MaxCount=MaxCount, KeyName=KeyName, InstanceType=InstanceType)

        ins_id = re.compile("'(.*)'").findall(str(ins[0]))[0]

    def filter(self, status):
        instances = self.conn.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': status}])
        ins_id = []
        for instance in instances:
            ins_id.append(instance.id)
        return ins_id

    def get_instances(self):
        # have not check the stopping
        print 'Running instances :   '
        print self.filter(['running'])

        print '\nStopped instances: '
        print self.filter(['stopped'])

        ing=self.filter(['stopping','pending','shutting-down'])
        if ing:
        	print   'processing instances:'
        	print ing
    def get_ids(self):

        return self.ids

    def start_all(self):
        id_list = self.filter(['running', 'stopped', 'stopping'])
        if(id_list):
            self.conn.instances.filter(InstanceIds=id_list).start()

    def stop_all(self):
        id_list = self.filter(['running'])
        if(id_list):
            self.conn.instances.filter(InstanceIds=id_list).stop()

    def terminate_all(self):
        instances = self.conn.instances.filter(
            Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}])
        id_list = []
        for instance in instances:
            id_list.append(instance.id)
        if(id_list):
            self.conn.instances.filter(InstanceIds=id_list).terminate()

    def start(self, ins_id):
        ins_idlist = []
        ins_idlist.append(ins_id)
        self.conn.instances.filter(InstanceIds=ins_idlist).start()

    def stop(self, ins_id):
        ins_idlist = []
        ins_idlist.append(ins_id)
        self.conn.instances.filter(InstanceIds=ins_idlist).stop()

    def create_image(self):
        self.image = create_image(instance_id, name)


class schedule(object):

    def __init__(self, *args, **kwargs):
        self.restart_duration = 300
        self.num = num
        self.ids = ids

    def control(self):
        now = time.time()
        while(1):
            run_all()
            time.sleep(self.restart_duration)
            stop_all()
            if ():
                break
            pass

a = EC2manager()
a.get_connected()


"""
a.create_instances()
"""
a.get_instances()
a.start_all()

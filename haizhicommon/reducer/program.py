#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# Don't import library if library not in client side.

from __future__ import print_function, division

import boto3

from awsapi.secret import AWS_ACCESS_ID, AWS_SECRET_KEY

REGION_NAME = 'ap-northeast-1'
BUCKET = 'chem-json'
HOMEDIR = '/home/admin/chemnet'

S3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_ID, aws_secret_access_key=AWS_SECRET_KEY)


def save_bucket(bucketname, savepath):
    """ import must write in function to support this framework.
    """
    import os
    import hashlib
    global S3

    count = 0
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    bucket = S3.Bucket(bucketname)
    wfname = os.path.join(savepath, bucketname+str(index))
    with open(wfname, 'w') as fd:

        for i in bucket.objects.all():
            hashint = int(hashlib.sha1(i.key).hexdigest(), 16)
            if hashint % machine_num == index:
                content = i.get()['Body'].read()
                fd.write(content)
                fd.write('\n')
                count += 1
            if count & 4095 == 0:
                print(count)
    os.system('eval `ssh-agent -s`; chmod 600 /home/admin/.ssh/crawl-tokyo.pem; ssh-add /home/admin/.ssh/crawl-tokyo.pem; scp -o StrictHostKeyChecking=no {} admin@172.31.19.253:/data/searchzhidao/'.format(wfname))


def fake_save_bucket(bucketname, savepath):
    print('fake save_bucket works!')
    print(type(index), index, machine_num)


save_bucket(BUCKET, HOMEDIR)

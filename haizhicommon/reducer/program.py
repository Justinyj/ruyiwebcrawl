#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# Don't import library if library not in client side.

from __future__ import print_function, division

import boto3
import json
import hashlib

from awsapi.secret import AWS_ACCESS_ID, AWS_SECRET_KEY

REGION_NAME = 'ap-northeast-1'
BUCKET = 'searchzhidao-json'
HOMEDIR = '/home/admin/'

S3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_ID, aws_secret_access_key=AWS_SECRET_KEY)


def save_bucket(bucketname, savepath, index, total):
    index = int(index)
    if not os.path.exists(savepath):
        os.makedirs(savepath)

    bucket = S3.Bucket(bucketname)
    with open(os.path.join(savepath, bucketname), 'w') as fd:
        for i in bucket.objects.all():
            hashint = int(hashlib.sha1(i.key).hexdigest(), 16)
            if hashint % total == index:
                content = i.get()['Body'].read()
                fd.write(content)
                fd.write('\n')

def fake_save_bucket(bucketname, savepath):
    print('fake save_bucket works!')
    print(index, machine_num)

save_bucket(BUCKET, HOMEDIR)

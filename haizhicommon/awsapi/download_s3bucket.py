#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import boto3
import os
from datetime import datetime


REGION_NAME = 'ap-northeast-1'
if REGION_NAME == 'ap-northeast-1':
    from secret import AWS_ACCESS_ID_TK as AWS_ACCESS_ID, AWS_SECRET_KEY_TK as AWS_SECRET_KEY
elif REGION_NAME == 'cn-north-1':
    from secret import AWS_ACCESS_ID_BJ as AWS_ACCESS_ID, AWS_SECRET_KEY_BJ as AWS_SECRET_KEY


S3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_ID, aws_secret_access_key=AWS_SECRET_KEY)


def count_bucket(bucketname):
    total = 0
    bucket = S3.Bucket(bucketname)
    for i in bucket.objects.all():
        total += 1
    print(total)


def delete_bucket(bucketname):
    bucket = S3.Bucket(bucketname)
    bucket.objects.delete()


def empty_bucket(bucketname, compare_time=None):
    """ compare_time, delete object older than this time
    :param compare_time: datetime(2016,7,1,2,0,0,).strftime('%Y%m%d%H%M%S') 
    """
    bucket = S3.Bucket(bucketname)
    for i in bucket.objects.all():
        if compare_time:
            if i.last_modified.strftime('%Y%m%d%H%M%S') < compare_time:
                i.delete()
        else:
            i.delete()


def save_to_local(bucketname):
    if not os.path.exists(bucketname):
        os.makedirs(bucketname)

    total = 0
    bucket = S3.Bucket(bucketname)
    for i in bucket.objects.all():
        fdir = os.path.join(bucketname, i.key[-1])
        if not os.path.exists(fdir):
            os.makedirs(fdir)

        fname = os.path.join(fdir, i.key)
        if os.path.exists(fname):
            continue
        try:
            content = i.get()['Body'].read()
            with open(fname, 'w') as fd:
                fd.write(content)
        except Exception as e:
            print(e)
        finally:
            total += 1

        if total & 8191 == 0:
            print('{}: {}'.format(datetime.now().isoformat(), total))


def down_fudankg(bucketname):
    bucket = S3.Bucket(bucketname)
    for i in bucket.objects.all():
        fdir = os.path.join(bucketname, i.key[-1])
        if not os.path.exists(fdir):
            os.makedirs(fdir)
        content = i.get()['Body'].read()
        with open(os.path.join(fdir, i.key), 'w') as fd:
            fd.write(content)


if __name__ == '__main__':
    bucketname = 'fudankg-json'
    compare_time = datetime(2016,7,1,2,0,0,).strftime('%Y%m%d%H%M%S') 
    count_bucket('dongcaigonggao-yy2')

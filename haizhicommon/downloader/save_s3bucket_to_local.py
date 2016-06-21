#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import boto3

from secret import AWS_ACCESS_ID, AWS_SECRET_KEY
from settings import REGION_NAME

S3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_ID, aws_secret_access_key=AWS_SECRET_KEY)


def save_to_local(bucketname):
    total = 0
    bucket = S3.Bucket(bucketname)
    for i in bucket.objects.all():
        try:
            content = i.get()['Body'].read()
            with open(bucketname + '/' + i.key, 'w') as fd:
                fd.write(content)
        except Exception as e:
            print(e)
        finally:
            total += 1


if __name__ == '__main':
    bucketname = 'dongcaigonggao'
    save_to_local(bucketname)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import boto3
import botocore

from secret import EC2_ACCESS_ID, EC2_SECRET_KEY

REGION_NAME = 'ap-northeast-1'


S3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=EC2_ACCESS_ID, aws_secret_access_key=EC2_SECRET_KEY)

def ensure_bucket(batch_key):
    if not hasattr(ensure_bucket, '_auth'):
        setattr(ensure_bucket, '_auth', bucketmanager_handler)

    try:
        S3.meta.client.head_bucket(Bucket=batch_key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            S3.create_bucket(Bucket=batch_key, CreateBucketConfiguration={'LocationConstraint': REGION_NAME})


def s3_get_cache(batch_id, url_hash):
    pass

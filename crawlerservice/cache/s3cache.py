#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import boto3
import botocore
import string
import base64
import json

from datetime import datetime

from dbconnector import dbwrapper
from secret import AWS_ACCESS_ID, AWS_SECRET_KEY
from tools import cachelog
from settings import REGION_NAME


S3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_ID, aws_secret_access_key=AWS_SECRET_KEY)

def ensure_bucket(batch_key):
    try:
        S3.meta.client.head_bucket(Bucket=batch_key)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == '404':
            create_bucket(batch_key)

def create_bucket(batch_key):
    for _ in range(3):
        try:
            return S3.create_bucket(Bucket=batch_key, CreateBucketConfiguration={'LocationConstraint': REGION_NAME})
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                pass
            elif e.response['Error']['Code'] == 'OperationAborted':
                continue
            elif e.response['Error']['Code'] == 'InvalidBucketName':
                return e.response['Error']['Code']


def s3_get_cache(batch_id, url_hash, exists=False):

    def get_cache(batch_key, filename):
        try:
            streaming_body = S3.Object(batch_key, filename).get()
            content = streaming_body[u'Body'].read()
        except botocore.exceptions.ClientError as e:
            # NoSuchKey, NoSuchBucket
            return {'error': e.response['Error']['Code']}
        return {'content': content}

    def head_cache(batch_key, filename):
        try:
            S3.Object(batch_key, filename).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
        return True

    try:
        filename = '{}_{}'.format(batch_id, url_hash)
        batch_key = batch_id.rsplit('-', 1)[0]

        if exists:
            return {'success': True, 'exists': head_cache(batch_key, filename)}

        ret = get_cache(batch_key, filename)
        if 'error' in ret:
            return {'success': False, 'error': ret['error']}
    except Exception as e:
        return {'success': False, 'error': e}

    return {'success': True, 'content': ret['content']}



def s3_put_cache(b64url, url_hash, batch_id, groups, content, refresh=False):
    """
    :param groups: e.g. 'g1, g2'
    """

    def put_cache(batch_key, filename, content):
        try:
            ret = S3.Object(batch_key, filename).put(Body=content)
            if ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {'success': True}
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                ret = create_bucket(batch_key)
                if type(ret) == str:
                    return {'error': ret}

            return {'error': e.response['Error']['Code']}
        except Exception as e:
            return {'error': e}

    try:
        filename = '{}_{}'.format(batch_id, url_hash)
        batch_key = batch_id.rsplit('-', 1)[0]

        ret = put_cache(batch_key, filename, content)
        if 'error' in ret and ret['error'] == 'NoSuchBucket':
            ret = put_cache(batch_key, filename, content)
        if 'error' in ret:
            return {'success': False, 'error': ret['error']}

        _groups = str(map(string.strip, groups.split(',')))[1:-1].replace('\'', '"')
        sql1 = ("insert into accessed (batch_id, groups, status, b64url, url_hash) "
                "values ('{}', '{{{}}}', '{}', '{}', '{}');".format(batch_id, _groups, 0, b64url, url_hash))
        sql2 = ("insert into cached (b64url, url_hash) values ('{}', '{}')"
                ";".format(b64url, url_hash))
        dbwrapper.execute(sql1)
        dbwrapper.execute(sql2)

        now = datetime.now()
        log_line = json.dumps({
            'date': str(now),
            'batch_id': batch_id,
            'groups': groups,
            'url': base64.urlsafe_b64decode(b64url),
        })
        cachelog.get_logger(batch_id, now.strftime('%Y%m%d')).info(log_line)
    except Exception as e:
        return {'success': False, 'error': e}
    return {'success': True}


def delete_object(bucket, key):
    """ delete object in bucket """
    S3.Object(bucket, key).delete()
 
def bucket_contents(bucketname):
    """ list contents of bucket """
    bucket = S3.Bucket(bucketname)
    for key in bucket.objects.all():
        print(key)


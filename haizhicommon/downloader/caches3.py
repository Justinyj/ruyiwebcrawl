#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import boto3
import botocore
import hashlib

from secret import AWS_ACCESS_ID, AWS_SECRET_KEY
from settings import REGION_NAME

S3 = boto3.resource('s3', region_name=REGION_NAME, aws_access_key_id=AWS_ACCESS_ID, aws_secret_access_key=AWS_SECRET_KEY)

class CacheS3(object):
    def __init__(self, batch_id):
        self.batch_id = batch_id
        self.batch_key = batch_id.rsplit('-', 1)[0]


    def exists(self, url):
        url_hash = hashlib.sha1(url).hexdigest()
        filename = '{}_{}'.format(self.batch_id, url_hash)
        return self.head_cache(filename)


    def get(self, url):
        try:
            url_hash = hashlib.sha1(url).hexdigest()
            filename = '{}_{}'.format(self.batch_id, url_hash)
            ret = self.get_cache(filename)
            if 'error' in ret:
                return u''
        except Exception as e:
            return u''

        return ret['content']


    def post(self, url, content, groups=None, refresh=False):
        try:
            url_hash = hashlib.sha1(url).hexdigest()
            filename = '{}_{}'.format(self.batch_id, url_hash)
            ret = self.put_cache(filename, content)
            if 'error' in ret and ret['error'] == 'NoSuchBucket':
                ret = self.put_cache(filename, content)
            if 'error' in ret:
                return ret['error']
        except Exception as e:
            return e
        return True


    def get_cache(self, filename):
        try:
            streaming_body = S3.Object(self.batch_key, filename).get()
            content = streaming_body[u'Body'].read()
        except botocore.exceptions.ClientError as e:
            # NoSuchKey, NoSuchBucket
            return {'error': e.response['Error']['Code']}
        return {'content': content}


    def head_cache(self, filename):
        try:
            S3.Object(self.batch_key, filename).load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
        return True

    def put_cache(self, filename, content):
        try:
            ret = S3.Object(self.batch_key, filename).put(Body=content)
            if ret['ResponseMetadata']['HTTPStatusCode'] == 200:
                return {'success': True}
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucket':
                ret = self.create_bucket()
                if type(ret) == str:
                    return {'error': ret}

            return {'error': e.response['Error']['Code']}
        except Exception as e:
            return {'error': e}

    def create_bucket(self):
        for _ in range(3):
            try:
                return S3.create_bucket(Bucket=self.batch_key, CreateBucketConfiguration={'LocationConstraint': REGION_NAME})
            except botocore.exceptions.ClientError as e:
                if e.response['Error']['Code'] == 'BucketAlreadyOwnedByYou':
                    pass
                elif e.response['Error']['Code'] == 'OperationAborted':
                    continue
                elif e.response['Error']['Code'] == 'InvalidBucketName':
                    return e.response['Error']['Code']

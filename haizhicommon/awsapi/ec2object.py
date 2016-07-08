#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import boto3

from .secret import AWS_ACCESS_ID, AWS_SECRET_KEY

class Ec2object(object):

    def __init__(self, region_name='ap-northeast-1'):
        self.ec2 = boto3.resource('ec2', region_name=region_name, aws_access_key_id=AWS_ACCESS_ID, aws_secret_access_key=AWS_SECRET_KEY)



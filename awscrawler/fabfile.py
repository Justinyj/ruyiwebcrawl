#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from fabric.api import *

env.hosts = ['52.53.180.142']
env.user = 'admin'

DEPLOY_ENV = 'TEST'

def _aws():
    sudo('mkfs -t ext4 /dev/xvdb')
    sudo('mkdir /data')
    sudo('mount /dev/xvdb /data')
    sudo('cp /etc/fstab /etc/fstab.orig')
    sudo("""sh -c "echo '/dev/xvdb /data ext4 defaults,nofail 0 2' > /etc/fstab" """)


def build_env():
    sudo('apt-get -y install libcurl4-gnutls-dev libghc-gnutls-dev python-pip python-dev dtach')
    sudo('pip install virtualenvwrapper')
    sudo('apt-get -y install redis-server')

def upload():
    archive = 'awscrawler.tar.bz2'
    with lcd('..'):
        local('tar jcf {} --exclude *.pyc awscrawler'.format(archive))
        put('{}'.format(archive), '/tmp/')
        put('~/.ssh/crawler-california.pem', '/home/.ssh/')

    with cd('/tmp'):
        run('tar jxf /tmp/{}'.format(archive))
        sudo('mkdir -p /opt/service/awsframe; chown -R {user}:{user} /opt/service'.format(user=env.user))
        run('mv /tmp/awscrawler /opt/service/awsframe/awscrawler`date +%Y%m%d%H%M%S`')

    with cd('/opt/service/'):
        run('[ -L awscrawler ] && unlink awscrawler || echo ""')
        run('ln -s /opt/service/awsframe/`ls /opt/service/awsframe/ | sort | tail -n 1` /opt/service/awscrawler')

def kill():
    run("ps aux | grep python | grep -v grep | grep awscrawler | awk '{print $2}' | xargs -n 1 --no-run-if-empty kill")
    run('[ -e /tmp/awscrawler.sock ] && rm /tmp/awscrawler.sock || echo "no /tmp/awscrawler.sock"')

def runapp():
    with cd('/opt/service/awscrawler'):
        run('source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv awscrawler')
        with prefix('source env.sh {}'.format(DEPLOY_ENV)):
            run('pip install -r requirements.txt')
            run('dtach -n /tmp/{}.sock {}'.format('awscrawler', 'python main.py'))

def deploy():
    upload()
    kill()
    runapp()

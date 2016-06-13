#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from fabric.api import *

env.hosts = ['52.196.166.54']
env.hosts = ['52.193.140.89']
env.user = 'admin'

DEPLOY_ENV = 'PRODUCTION'

def _aws():
    """ main server need 200G disk for cache logging
        lots of memory for redis
    """
    sudo('mkfs -t ext4 /dev/xvdb')
    sudo('mkdir /data')
    sudo('mount /dev/xvdb /data')
    sudo('cp /etc/fstab /etc/fstab.orig')
    sudo("""sh -c "echo '/dev/xvdb /data ext4 defaults,nofail 0 2' >> /etc/fstab" """)


def build_env():
    sudo('apt-get update')
    sudo('apt-get -y install libcurl4-gnutls-dev libghc-gnutls-dev python-pip python-dev dtach')
    sudo('apt-get -y install libssl-dev')
    sudo('pip install virtualenvwrapper')
#    sudo('apt-get -y install redis-server') # worker not needed
#    sudo('sed -i "s/bind 127.0.0.1/bind 0.0.0.0/" /etc/redis/redis.conf')
#    sudo('/etc/init.d/redis-server restart')

def upload():
    archive = 'awscrawler.tar.bz2'
    with lcd('..'):
        local('tar jcf {} --exclude *.pyc awscrawler'.format(archive))
        put('{}'.format(archive), '/tmp/')
        put('~/.ssh/crawl-tokyo.pem', '/home/admin/.ssh/')

    with cd('/tmp'):
        run('tar jxf /tmp/{}'.format(archive))
        sudo('mkdir -p /opt/service/awsframe; chown -R {user}:{user} /opt/service'.format(user=env.user))
        run('mv /tmp/awscrawler /opt/service/awsframe/awscrawler`date +%Y%m%d%H%M%S`')

    with cd('/opt/service/'):
        run('[ -L awscrawler ] && unlink awscrawler || echo ""')
        run('ln -s /opt/service/awsframe/`ls /opt/service/awsframe/ | sort | tail -n 1` /opt/service/awscrawler')
        with cd('awsframe'):
            run('ls -tp | grep -v "/$" | tail -n +6 | xargs -I {} rm -- {}')

def kill():
    run("ps aux | grep python | grep -v grep | grep awscrawler | awk '{print $2}' | xargs -n 1 --no-run-if-empty kill")
    run('[ -e /tmp/awscrawler.sock ] && rm /tmp/awscrawler.sock || echo "no /tmp/awscrawler.sock"')

def runapp():
    with cd('/opt/service/awscrawler'):
        run('source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv awscrawler')
        with prefix('source env.sh {}'.format(DEPLOY_ENV)):
            run('pip install -r requirements.txt')
#            run('dtach -n /tmp/{}.sock {}'.format('awscrawler', 'python invoker/zhidao.py'))

def deploy():
    upload()
    kill()
    runapp()

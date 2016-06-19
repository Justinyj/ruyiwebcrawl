#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from fabric.api import *

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
        local("dirtime=`date +%Y%m%d%H%M%S`; mkdir awscrawler$dirtime; cp -r awscrawler/* awscrawler$dirtime; cp -r haizhicommon/downloader haizhicommon/parsers haizhicommon/rediscluster awscrawler$dirtime; tar jcf {} --exclude='*.pyc' awscrawler$dirtime; rm -r awscrawler$dirtime".format(archive))
        put('{}'.format(archive), '/tmp/')
        put('~/.ssh/crawl-tokyo.pem', '/home/admin/.ssh/')

    with cd('/tmp'):
        sudo('mkdir -p /opt/service/awsframe; chown -R {user}:{user} /opt/service'.format(user=env.user))
        run('tar jxf /tmp/{} -C /opt/service/awsframe/'.format(archive))

    with cd('/opt/service/'):
        run('[ -L awscrawler ] && unlink awscrawler || echo ""')
        run('ln -s /opt/service/awsframe/`ls /opt/service/awsframe/ | sort | tail -n 1` /opt/service/awscrawler')
        with cd('awsframe'):
            run('ls -tp | tail -n +6 | xargs -I {} rm -r -- {}')

def kill():
    run("ps aux | grep python | grep -v grep | grep awscrawler | awk '{print $2}' | xargs -n 1 --no-run-if-empty kill")
    run('[ -e /tmp/awscrawler.sock ] && rm /tmp/awscrawler.sock || echo "no /tmp/awscrawler.sock"')

def runapp(flag_run, job):
    with cd('/opt/service/awscrawler'):
        run('source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv awscrawler')
        with prefix('source env.sh {}'.format(DEPLOY_ENV)):
            run('pip install -r requirements.txt')
            if flag_run:
                run('dtach -n /tmp/{}.sock {}'.format('awscrawler', 'python invoker/{}.py'.format(job)))

def sync_upload():
    local("rsync -azvrtopg -e 'ssh '  local  admin@{}:/data/awscrawler".format(env.hosts[0]))


def deploy_worker():
    # fab deploy_worker --hosts 52.69.119.200
#    env.hosts = [host]
    print (env.hosts)
    upload()
    kill()
    runapp(False, None)

def deploy_run(job):
    # fab deploy_run:'prefetch_zhidao_search' --hosts 52.196.166.54
    print (job)
#    env.hosts = ['52.196.166.54']
    sync_upload()
    upload()
    kill()
    runapp(True, job)

def debug(host):
    env.hosts = [host]
    #fab test:'192.1.1.1:123'
    #http://stackoverflow.com/questions/8960777/pass-parameter-to-fabric-task
    print (host)
    sync_upload()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from fabric.api import *
from settings import DBPASS

hostos = 'debian'
if hostos == 'ubuntu':
    env.hosts = ['106.75.6.152']
    env.user = 'ubuntu'
    PG_VERSION = 'trusty-pgdg'
elif hostos == 'debian':
    env.hosts = ['54.183.222.55']
    env.user = 'admin'
    PG_VERSION = 'jessie-pgdg'

DEPLOY_ENV = 'ZHIDAO'

def _aws():
    sudo('mkfs -t ext4 /dev/xvdb')
    sudo('mkdir /data')
    sudo('mount /dev/xvdb /data')
    sudo('cp /etc/fstab /etc/fstab.orig')
    sudo("""sh -c "echo '/dev/xvdb /data ext4 defaults,nofail 0 2' > /etc/fstab" """)

def _build_pg():
    sudo('touch /etc/apt/sources.list.d/pg.list')
    sudo("""sh -c "echo 'deb http://apt.postgresql.org/pub/repos/apt/ {} main' > /etc/apt/sources.list.d/pg.list" """.format(PG_VERSION))
    sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')
    sudo('apt-get update')
    sudo('apt-get -y install postgresql-server-dev-9.5 postgresql')
    sudo('mkdir -p /data/pg; chown -R postgres:postgres /data/pg')
    sudo('mkdir -p /data/crawler_file_cache/; chown -R {user}:{user} /data/crawler_file_cache'.format(user=env.user))
    sudo('sed -i "s/postgres\ *peer/postgres           trust/" /etc/postgresql/9.5/main/pg_hba.conf')
    sudo("""sed -i "s/'\/var\/lib\/postgresql\/9.5\/main'/'\/data\/pg\/main'/" /etc/postgresql/9.5/main/postgresql.conf""")
    sudo('mv /var/lib/postgresql/9.5/main /data/pg/')
    sudo('service postgresql restart')
    sudo("""sudo -u postgres psql -c "ALTER USER postgres PASSWORD '{}';" """.format(DBPASS))


def build_env():
    _build_pg()
    sudo('apt-get -y install libcurl4-gnutls-dev libghc-gnutls-dev python-pip python-dev dtach')
    sudo('pip install virtualenvwrapper')


def upload():
    archive = 'crawlerservice.tar.bz2'
    with lcd('..'):
        local('tar jcf {} --exclude *.pyc crawlerservice'.format(archive))
        put('{}'.format(archive), '/tmp/')

    with cd('/tmp'):
        run('tar jxf /tmp/{}'.format(archive))
        sudo('mkdir -p /opt/service/raw; chown -R {user}:{user} /opt/service'.format(user=env.user))
        run('mv /tmp/crawlerservice /opt/service/raw/crawlerservice`date +%Y%m%d%H%M%S`')

    with cd('/opt/service/'):
        run('[ -L crawlerservice ] && unlink crawlerservice || echo ""')
        run('ln -s /opt/service/raw/`ls /opt/service/raw/ | sort | tail -n 1` /opt/service/crawlerservice')


def kill():
    run("ps aux | grep python | grep -v grep | awk '{print $2}' | xargs -n 1 --no-run-if-empty kill")
    run('[ -e /tmp/*.sock ] && rm /tmp/*.sock || echo "no /tmp/*.sock"')

def runapp():
    with cd('/opt/service/crawlerservice'):
#        run('psql -U postgres < cache/crawlercache.sql')
        run('source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv crawlerservice')
        with prefix('source env.sh {}'.format(DEPLOY_ENV)):
            run('pip install -r requirements.txt')
            run('dtach -n /tmp/{}.sock {}'.format('crawlercache', 'python main.py -port=8000 -process=4 -program=cache'))
#            run('dtach -n /tmp/{}.sock {}'.format('crawlerproxy', 'python main.py -port=8001 -process=1 -program=proxy'))
#            run('dtach -n /tmp/{}.sock {}'.format('crawlerfetch', 'python main.py -port=8002 -process=4 -program=fetch'))


def deploy():
    upload()
    kill()
    runapp()


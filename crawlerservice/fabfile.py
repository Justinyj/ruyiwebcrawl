#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from fabric.api import *
from settings import DBPASS

env.hosts = ['106.75.6.152']
env.user = 'ubuntu'

def _build_pg():
    sudo('touch /etc/apt/sources.list.d/pg.list')
    sudo("""sh -c "echo 'deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main' > /etc/apt/sources.list.d/pg.list" """)
    sudo('wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -')
    sudo('apt-get update')
    sudo('apt-get -y install postgresql-server-dev-9.5 postgresql')
    sudo('mkdir -p /data/pg; chown -R postgres:postgres /data/pg')
    sudo('sed -i "s/postgres\ *peer/postgres           trust/" /etc/postgresql/9.5/main/pg_hba.conf')
    sudo("""sed -i "s/'\/var\/lib\/postgresql\/9.5\/main'/'\/data\/pg\/main'/" /etc/postgresql/9.5/main/postgresql.conf""")
    sudo('mv /var/lib/postgresql/9.5/main /data/pg/')
    sudo('service postgresql restart')
    sudo("""sudo -u postgres psql -c "ALTER USER postgres PASSWORD '{}';" """.format(DBPASS))


def build_env():
    _build_pg()
    sudo('sudo apt-get -y install libcurl4-gnutls-dev libghc-gnutls-dev python-pip python-dev dtach')
    sudo('sudo pip install virtualenvwrapper')


def upload():
    archive = 'crawlerservice.tar.bz2'
    with lcd('..'):
        local('tar jcf {} --exclude *.pyc crawlerservice'.format(archive))
        put('{}'.format(archive), '/tmp/')

    with cd('/tmp'):
        run('tar jxf /tmp/{}'.format(archive))
        sudo('mkdir -p /opt/service/raw; chown -R ubuntu:ubuntu /opt/service')
        run('mv /tmp/crawlerservice /opt/service/raw/crawlerservice`date +%Y%m%d%H%M%S`')

    with cd('/opt/service/'):
        run('[ -L crawlerservice ] && unlink crawlerservice || echo ""')
        run('ln -s /opt/service/raw/`ls /opt/service/raw/ | sort | tail -n 1` /opt/service/crawlerservice')


def deploy():
    upload()

    with cd('/opt/service/crawlerservice'):
#        run('psql -U postgres < cache/crawlercache.sql')
        run('source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv crawlerservice')
        with prefix('source env.sh {}'.format('PRODUCTION')):
            run('pip install -r requirements.txt')
            run('dtach -n /tmp/{}.sock {}'.format('crawlerproxy', 'python main.py'))
            run('dtach -n /tmp/{}.sock {}'.format('crawlercache', 'python main.py -port=8000 -process=4'))


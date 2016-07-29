#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from fabric.api import *

env.user = 'admin'
DEPLOY_ENV = 'PRODUCTION'

def upload():
    archive = 'reducer.tar.bz2'
    prog = 'reducer'
    prog_dir = 'reducerraw'
    with lcd('..'):
        local("dirtime=`date +%Y%m%d%H%M%S`; mkdir {prog}$dirtime; cp -r {prog}/* {prog}$dirtime; cp -r awsapi {prog}$dirtime; tar jcf {archive} --exclude='*.pyc' {prog}$dirtime; rm -r {prog}$dirtime".format(prog=prog, archive=archive))
        put('{}'.format(archive), '/tmp/')
        put('~/.ssh/crawl-tokyo.pem', '/home/admin/.ssh/')

    with cd('/tmp'):
        sudo('mkdir -p /opt/service/{prog_dir}; chown -R {user}:{user} /opt/service'.format(prog_dir=prog_dir, user=env.user))
        run('tar jxf /tmp/{archive} -C /opt/service/{prog_dir}/'.format(archive=archive, prog_dir=prog_dir))

    with cd('/opt/service/'):
        run('[ -L {prog} ] && unlink {prog} || echo ""'.format(prog=prog))
        run('ln -s /opt/service/{prog_dir}/`ls /opt/service/{prog_dir}/ | sort | tail -n 1` /opt/service/{prog}'.format(prog_dir=prog_dir, prog=prog))
        with cd(prog_dir):
            run('ls -tp | tail -n +6 | xargs -I {} rm -r -- {}')


def runapp(flag_run=True, param=None):
    prog = 'reducer'
    with cd('/opt/service/{}'.format(prog)):
        run('source /usr/local/bin/virtualenvwrapper.sh; mkvirtualenv {}'.format(prog))
        with prefix('source env.sh {}'.format(DEPLOY_ENV)):
            run('pip install -r requirements.txt')
            if flag_run:
                run('dtach -n /tmp/{}.sock {}'.format(prog, 'python controller.py -b searchzhidao2-json-20160728 -m 100 -p program.py'))


def deploy_worker():
    upload()
    runapp(False, None)

def deploy_run():
    upload()
    runapp(True, None)

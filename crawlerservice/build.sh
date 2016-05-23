#!/bin/bash
if [[ `uname` == 'Linux' ]]; then
    sudo touch /etc/apt/sources.list.d/pg.list
    sudo sh -c "echo 'deb http://apt.postgresql.org/pub/repos/apt/ trusty-pgdg main' > /etc/apt/sources.list.d/pg.list"
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
    sudo apt-get update
    sudo apt-get -y install postgresql-server-dev-9.5 postgresql python-pip
    sudo apt-get -y install libcurl4-gnutls-dev libghc-gnutls-dev
    sudo pip install virtualenvwrapper
fi

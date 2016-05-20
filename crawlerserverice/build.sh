#!/bin/bash
if [[ `uname` == 'Linux' ]]; then
    sudo apt-get install postgresql-server-dev-9.4 postgresql
    sudo apt-get install libcurl4-gnutls-dev libghc-gnutls-dev
fi

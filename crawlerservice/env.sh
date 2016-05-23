#!/bin/bash
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
UDIR="$( cd cache && pwd )"
export PYTHONPATH=$DIR:$UDIR:$PYTHONPATH
export ENV=$1
source /usr/local/bin/virtualenvwrapper.sh
workon crawlerservice

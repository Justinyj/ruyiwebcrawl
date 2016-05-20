#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 test"
    exit
fi

if [ "$1" = "init" ]; then
  echo "sudo pip install virtualenvwrapper"
  echo "source /usr/local/bin/virtualenvwrapper.sh"
  echo "mkvirtualenv qichacha"
  echo "source env.sh"
  echo "pip install -r requirments.txt"
fi

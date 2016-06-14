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

if [ "$1" = "search" ]; then
  source env.sh
  python business/crawljob.py search medical
fi

if [ "$1" = "aws-init" ]; then
  # i-da8fef45

  # ssh -i ~/.ssh/crawl-tokyo.pem ubuntu@52.196.223.131

  # sudo  mkdir /data
  # sudo chown ubuntu /data
  # mkdir -p /data/ruyi/ruyiwebcrawl/projects/qichacha




  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  /Users/lidingpku/haizhi/project/ruyiwebcrawl/local/qichacha/business/work admin@52.69.161.139:/data/ruyi/ruyiwebcrawl/local/qichacha/business
  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  /Users/lidingpku/haizhi/project/ruyiwebcrawl/local/qichacha/business/server admin@52.69.161.139:/data/ruyi/ruyiwebcrawl/local/qichacha/business


  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  admin@52.69.161.139:/data/crawler_file_cache/qichacha_fetch_20160603 /data/crawler_file_cache
  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  admin@52.69.161.139:/data/crawler_file_cache/qichacha_search_20160603 /data/crawler_file_cache
  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  admin@52.69.161.139:/data/crawler_file_cache/qichacha_json_20160603 /data/crawler_file_cache

  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  /data/crawler_file_cache/qichacha_search_20160603 admin@52.69.161.139:/data/crawler_file_cache/

  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  *  ubuntu@52.196.223.131:/data/ruyi/ruyiwebcrawl/projects/qichacha
  echo "ssh -p50001 data@52.196.223.131"
fi

if [ "$1" = "aws-server-up" ]; then
  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  /Users/lidingpku/haizhi/project/ruyiwebcrawl/projects admin@52.69.161.139:/data/ruyi/ruyiwebcrawl/
  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  /Users/lidingpku/haizhi/project/ruyiwebcrawl/local/qichacha/business/input admin@52.69.161.139:/data/ruyi/ruyiwebcrawl/local/qichacha/business
fi

if [ "$1" = "aws-server-down" ]; then
  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  admin@52.69.161.139:/data/ruyi/ruyiwebcrawl/local/qichacha/business/server /Users/lidingpku/haizhi/project/ruyiwebcrawl/local/qichacha/business
  rsync -azvrtopg -e 'ssh -i /Users/lidingpku/.ssh/crawl-tokyo.pem'  admin@52.69.161.139:/data/ruyi/ruyiwebcrawl/local/qichacha/business/server_output /Users/lidingpku/haizhi/project/ruyiwebcrawl/local/qichacha/business
fi


if [ "$1" = "upload" ]; then
  rsync -azvrtopg -e 'ssh -p50001'  ./local  data@106.75.14.79:/data/ruyi/ruyiwebcrawl/projects/qichacha
  echo "ssh -p50001 data@106.75.14.79"
fi

if [ "$1" = "download" ]; then
  rsync -azvrtopg -e 'ssh  -p50001'   data@106.75.14.79:/data/ruyi/ruyiwebcrawl/projects/qichacha/local .
  echo "ssh -p50001 data@106.75.14.79"
fi


if [ "$1" = "cache-up" ]; then
#  rsync -azvrtopg -e 'ssh -p50001'  /data/crawler_file_cache/qichacha0601search  data@106.75.14.79:/data/crawler_file_cache
#  rsync -azvrtopg -e 'ssh'  /data/crawler_file_cache/qichacha0601search  lidingpku@wukong:/data/crawler_file_cache
#  rsync -azvrtopg -e 'ssh -p50001'  /data/crawler_file_cache/qichacha0601fetch  data@106.75.14.79:/data/crawler_file_cache

  rsync -azvrtopg -e 'ssh -p50001'  /data/crawler_file_cache/qichacha_fetch_20160603  data@106.75.14.79:/data/crawler_file_cache
  rsync -azvrtopg -e 'ssh -p50001'  /data/crawler_file_cache/qichacha_search_20160603  data@106.75.14.79:/data/crawler_file_cache
  echo "ssh -p50001 data@106.75.14.79"
fi

if [ "$1" = "cache-down" ]; then
  rsync -azvrtopg -e 'ssh -p50001'   data@106.75.14.79:/data/crawler_file_cache /data
  echo "ssh -p50001 data@106.75.14.79"
fi

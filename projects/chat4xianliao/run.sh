#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 test"
    exit
fi

if [ "$1" = "aws-init-image" ]; then
  python hzlib/api_aws.py chat4xianliao_image list
#  python hzlib/api_aws.py chat4xianliao_image start 1
#  python hzlib/api_aws.py chat4xianliao_image stop
  python hzlib/api_aws.py chat4xianliao_image local 1 chat4xl_up
fi

if [ "$1" = "aws-image-down" ]; then
  python hzlib/api_aws.py chat4xianliao_image local 1 chat4xl_down
fi

if [ "$1" = "aws-list" ]; then
  python hzlib/api_aws.py chat4xianliao_worker list
fi

if [ "$1" = "aws-state" ]; then
  python hzlib/api_aws.py chat4xianliao_worker server 50 common_test ~/.ssh/crawl-tokyo.pem
fi

if [ "$1" = "aws-create" ]; then
  python hzlib/api_aws.py chat4xianliao_worker create 50
fi

# python -u /opt/data/ruyi/ruyiwebcrawl/projects/chat4xianliao/chat/task_run.py fetch {worker_id} {worker_num}
if [ "$1" = "aws-start" ]; then
  python hzlib/api_aws.py chat4xianliao_worker local 10 chat4xl_up
  python hzlib/api_aws.py chat4xianliao_worker start 10

fi

if [ "$1" = "aws-run" ]; then
  python hzlib/api_aws.py chat4xianliao_worker server 50 chat4xl_prefetch_search4intent ~/.ssh/crawl-tokyo.pem
fi

if [ "$1" = "aws-stop" ]; then
  python hzlib/api_aws.py chat4xianliao_worker stop 50
fi

if [ "$1" = "aws-upload-server" ]; then
  python hzlib/api_aws.py chat4xianliao_worker local 1 chat4xl_up 52.69.161.139
fi

if [ "$1" = "upload-local" ]; then
  rsync -azvrtopg -e 'ssh -p50001'  ../../local/haizhicommon  data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local
  rsync -azvrtopg -e 'ssh -p50001'  ../../local/chat4xianliao  data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local
#  rsync -azvrtopg -e 'ssh -p50001'  ../../local/chat4xianliao  data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local
  echo "ssh -p50001 data@106.75.14.79"
fi

if [ "$1" = "download-local" ]; then
  rsync -azvrtopg -e 'ssh  -p50001'   data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local/haizhicommon ../../local
  rsync -azvrtopg -e 'ssh  -p50001'   data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local/chat4xianliao ../../local
#  rsync -azvrtopg -e 'ssh  -p50001'   data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local/chat4xianliao ../../local
  echo "ssh -p50001 data@106.75.14.79"
fi

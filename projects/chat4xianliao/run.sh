#!/bin/sh

if [ $# -eq 0 ]; then
    echo "Usage: $0 test"
    exit
fi


if [ "$1" = "upload-local" ]; then
  rsync -azvrtopg -e 'ssh -p50001'  ../../local/haizhicommon  data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local
#  rsync -azvrtopg -e 'ssh -p50001'  ../../local/chat4xianliao  data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local
  echo "ssh -p50001 data@106.75.14.79"
fi

if [ "$1" = "download-local" ]; then
  rsync -azvrtopg -e 'ssh  -p50001'   data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local/haizhicommon ../../local
#  rsync -azvrtopg -e 'ssh  -p50001'   data@106.75.14.79:/data/ruyi/ruyiwebcrawl/local/chat4xianliao ../../local
  echo "ssh -p50001 data@106.75.14.79"
fi

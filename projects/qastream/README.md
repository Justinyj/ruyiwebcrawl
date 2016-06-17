## deploy
cd ../
scp -r qastream admin@52.192.116.149:/opt/service/projects 
cd ../
scp -r haizhicommon admin@52.192.116.149:/opt/service

sudo apt-get install libxml2-dev libxslt1-dev

## run
python receiver/main.py -port=8010

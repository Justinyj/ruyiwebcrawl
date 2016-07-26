from pymongo import MongoClient
import time,datetime
from unpack import unpack
from restore import restore

#crontab : 
#20 06 * * * /usr/bin/python2.7 /data/monitor/check/check.py  >> /data/monitor/check/cron_check.log

STANDARD_COLLECTION_LIST = [u'intentScenario', 
                            u'appModel', 
                            u'socialMatch', 
                            u'infoCollection', 
                            u'system.indexes', 
                            u'system.users', 
                            u'col_cache', 
                            u'authorizerModel', 
                            u'wxUserModel', 
                            u'wxMsgModel', 
                            u'systemPropertyModel', 
                            u'developerModel', 
                            u'action_items', 
                            u'entityModel', 
                            u'col_log', 
                            u'col_developer', 
                            u'intentModel', 
                            u'multiMediaModel']
def slack(msg):
        data={
            "text": msg
        }
        requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))

unpack()
restore()

client = MongoClient()
db = client.today
collection_list = db.collection_names()
flag_collection = (sorted(collection_list) == sorted(STANDARD_COLLECTION_LIST))
#print collection_list
#print STANDARD_COLLECTION_LIST

if  not flag_collection:
    slack ("Warning!collections did not match : supposed to be\n {} \n actually  is \n{}".format(STANDARD_COLLECTION_LIST, collection_list))
    print ("Warning!collections did not match : supposed to be\n {} \n actually  is \n{}".format(STANDARD_COLLECTION_LIST, collection_list))
    print "did not match!"
def check_time():
    for i in db['systemPropertyModel'].find({"_id" : "accessToken"}):
        time_now = datetime.datetime.now()
        time_log = datetime.datetime.fromtimestamp((i[u'gmtUpdate'])/1000)
        time_delta = time_now - time_log
        if time_delta.days > 3 :
            slack("your backup is out of date for {} days".format(time_delta.days))
            print("your backup is out of date for {} days".format(time_delta.days))

def statistic():
    counts = {}
    for i in collection_list :
        counts[i] = db[i].count()
    slack('DailyStatistic:{}'.format(json.dumps(counts)))
    return counts

#restore dirs : db_cache/  db_log/    db_ruyi/   db_wechat/ test/     admin looks like cannot restore?


check_time()
print statistic()
os.system('mongo < /data/monitor/check/deleteDatabase.js')
print "finished!"

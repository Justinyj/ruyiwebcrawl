# -*- coding: utf-8 -*-
# 脚本作用：从api列表里获取当天的天气json，并缓存到redis中
# 配合crontab命令可以实现每天3点定时更新，设置数据失效时间为21小时，即当天12点失效。
# redis结构：key为ruyi-action-heweather-cache，field是每个城市名和当天日期的组合，value是API返回的天气情况json
# 由于api每天调用次数有限，测试的时候谨慎修改代码。
# 每行api列表的格式是：  城市名    APIurl
import datetime
import redis
import requests

file_name = '/Users/johnson/my/cacnhe_city_list.txt'
KEY = 'ruyi-action-heweather-cache'
ip_179 = '192.168.1.179'
ip_10 ='10.10.84.141'

r = redis.Redis(host = ip_179, port=6379, db=0)

f = open(file_name, 'r')
citys = []
for line in f.readlines():
    try:
        city, url = line.strip().split('\t')[0], line.strip().split('\t')[1]
    except:
        print ('Invalid format for  {}'.format(line))
        continue
    citys.append((city, url))
f.close()

now =  datetime.datetime.now()
date = now.strftime("%Y-%m-%d")

# url = 'http://api.ruyi.ai/ruyi-action/weather2?location=上海&date='
# content = requests.get(url+date).text

count = 0
for item in citys:
    city, url = item[0],item[1]
    field = date+'_'+city
    content = f.requests.get(url+date)
    r.hset(KEY, field, content)

r.expire(KEY, 82800)  #3600*21
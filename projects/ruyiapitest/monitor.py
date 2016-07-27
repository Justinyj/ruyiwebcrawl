# -*- coding:utf-8 -*-
from secret import PUBLIC_KEY, PRIVATE_KEY
import hashlib
import urlparse
import urllib
import requests
import time
import string
import random
import json




backends = [
            {
                'test_url'   : '',
                'backend_id' : u'backend-ws42eq',
                'name'       : '01',
                'private_ip' : u'10.10.166.86',

            },
            {
                'test_url'   : '',
                'backend_id' : u'backend-vce245' ,
                'name'       : '02'   ,
                'private_ip' : u'10.10.177.183',
            }
]



def slack(msg):
    return
    data={
            "text": msg
    }
    requests.post("https://hooks.slack.com/services/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", data=json.dumps(data))

class UlbPolicyClient(object):
    def __init__(self, match):
        self.region = 'cn-bj2'
        self.public_key = PUBLIC_KEY
        self.private_key = PRIVATE_KEY
        self.domain = 'https://api.ucloud.cn/?'
        self.policy = None
        self.match = match
        #self.backends_ids = [u'backend-ws42eq', u'backend-vce245' ]
    
    
    def get_signature(self, paras):
        items = paras.items()
        items.sort()
        paras_data = ""
        for key, value in items:
            paras_data = paras_data + str(key) + str(value)
        paras_data = paras_data + self.private_key
        sign = hashlib.sha1()
        sign.update(paras_data)
        signature = sign.hexdigest()
        return signature


    def find_policy(self):
        paras = {
            'Action' : 'DescribePolicyGroup',
            'Region' : self.region,
            'PublicKey' : self.public_key,
        }
        signature = self.get_signature(paras)

        url = self.domain + urllib.urlencode(paras) +'&Signature={}'.format(signature)
        req = requests.get(url)
        item = req.json()
        # print item
        for group in item['DataSet']:     #uglyyyyyyyyyy!
            policy_set =  group['PolicySet']
            for policy in policy_set:
                if policy[u'Match'] == self.match:
                    self.policy = policy
                    break
            if self.policy:
                break
        else:
            print 'Could not find policy named {}!'.format(self.match)
            return False
        #print self.policy
        return True

    def update_policy_group_attribute(self):
        paras = {
            'Action' : 'UpdatePolicyGroupAttribute',
            'PublicKey' : self.public_key,
            'Region' : self.region,
            'GroupId': 'ulb-fr-2fw552',
        }
        signature = self.get_signature(paras)

        url = self.domain + urllib.urlencode(paras) +'&Signature={}'.format(signature)
        req = requests.get(url)

        if req.json()['RetCode'] == 0:
            return True
        else:
            return False

    def create_policy(self, backend):
        paras = {
            'Action'      : 'CreatePolicy',
            'Region'      : self.region, 
            'Match'       : self.match,                 
            'ULBId'       : 'ulb-t0yimg',#'ulb-b5ny4x' test的  ulb-t0yimg master
            'VServerId'   : 'vserver-c0jmgd',  # vserver-c0jmgd master  vserver-wuudxm test
            'GroupId'     : 'ulb-fr-2fw552',  #ulb-fr-2fw552 master  ulb-fr-qmwdgo test
            'BackendId.0' : backend[u'backend_id'], 
            'PublicKey'   : self.public_key, 
         }
        signature = self.get_signature(paras)
        url = self.domain + urllib.urlencode(paras) +'&Signature={}'.format(signature)
        req = requests.get(url)
        print req.json()
        if not req:
            return False
        if req.json()[u'RetCode'] != 0:
            return False
        return True

    def get_working_backend_id(self):
        if self.policy:
            backend_private_ip = self.policy[u'BackendSet'][0][u'PrivateIP']
            for item in backends:
                if item[u'private_ip'] == backend_private_ip:
                    return item
        return

    def get_policy_id(self):
        if self.policy:
            return self.policy[u'PolicyId']
        return

    def delete_policy(self):
        paras = {
            'Action' : 'DeletePolicy',
            'Region' : self.region,
            'GroupId': 'ulb-fr-2fw552',
            'PolicyId': self.get_policy_id(),
            'PublicKey': self.public_key,
        }
        if not paras['PolicyId']:
            return
        signature = self.get_signature(paras)
        url = self.domain + urllib.urlencode(paras) +'&Signature={}'.format(signature)

        req = requests.get(url)
        #print req.json()
        if req.json()[u'RetCode'] != 0:
            return False
        return False

    def update_policy(self, backend):
        paras = {
            'Action'      : 'UpdatePolicy',
            'Region'      : self.region,
            'PolicyId'    : self.get_policy_id(),
            'Match'       : self.match,
            'ULBId'       : 'ulb-t0yimg',
            'VServerId'   : 'vserver-c0jmgd',
            'BackendId.0' : backend[u'backend_id'], 
            'PublicKey'   : self.public_key,
            }
        if not paras['PolicyId']:
            return

        signature = self.get_signature(paras)
        url = self.domain + urllib.urlencode(paras) +'&Signature={}'.format(signature)
        req = requests.get(url)
        print url
        print req.json()
        if req.json()[u'RetCode'] != 0:
            return False
        return False

# m = UlbPolicyClient('ttttt')
# m.find_policy()
# m. update_policy(backends[1])
def random_url(url, length=4):
    chars = string.letters + string.digits
    s = ''.join(random.Random().sample(chars, length))
    return url.format(s)

def get_running_stat(url_temlate):
    url = random_url(url_temlate)
    for _ in range(3):
        response = requests.get(url)
        if response.status_code == 200:
            break
    else:
        return False
    res = response.json()
    process_milliseconds = res['result']['meta_process_milliseconds']

    return process_milliseconds

def get_another_backend(backend_id):
    for backend in backends:
        if backend['backend_id'] != backend_id:
            return backend

def convert_backend_toanoter(policy, working_ms):
    '''
    policy : 即转发策略,如api.ruyi.ao，在json里表示为Match
    有了转发策略的内容，还要通过一次find_policy定位到具体的某条策略上
    按照本程序的逻辑，如果policy根本不存在，还是会新建一条规则并转发到机器01上
    '''
    m1 = UlbPolicyClient(policy)
    m1.find_policy() 
    working_backend = m1.get_working_backend_id()[u'backend_id']

    m2 = UlbPolicyClient(policy)
    m2.create_policy(get_another_backend(working_backend))
    m1.delete_policy()

    id_for_human = {
        u'backend-ws42eq' : '01',
        u'backend-vce245' : '02',
    }
    msg = ('{} is in high process_milliseconds:{} ,the program just converted it into another').format(id_for_human[working_backend], working_ms)
    print msg
    slack(msg)
    return True


def main(policy_name):

    ms1 = get_running_stat(backends[0])
    ms2 = get_running_stat(backends[1])
    if ms1 == False :
        slack('Can not connect OK1!')
        return
    if ms2 == False :
        slack('Can not connect OK2!')
        return

    ok1 = ms1 < 500
    ok2 = ms2 < 500
    if ok1  and ok2 :
        print 'all right'
        # m = UlbPolicyClient(policy_name)
        # m.find_policy()
        # working_backend = m.get_working_backend_id()
        # if working_backend['name'] == '02':
        #     convert_backend_toanoter(policy_name)
        # slack('NOTICE : 01 and 02 are both in ok working status,just convert from 02 to 01 for{}'.format(policy_name))
        return
    if not ok1  and not ok2 :
        slack('both 01 and 02 are in high process_milliseconds:{};{}!Please check soon!'.format(ms1, ms2))
        print 'I have sent a bad messageeeeee'
        return
    #按照此逻辑，如果上面的检测中出现了一台高延迟，即使这是ULB后端的主机，在下面的判断中，如果再次测试状态正常，那么也不会进行调换
    #同样地，如果上面的检测中某台机器低延迟，另外一台高，如果低延迟的是ULB后端主机，在下面的判断中，再次测试状态异常，也会进行调换。
    rule = UlbPolicyClient(policy_name)
    if not rule.find_policy():      #不存在则新建
        rule.create_policy(backends[0])
        return
    working_backend = rule.get_working_backend_id()

    working_ms = get_running_stat(working_backend)
    if working_ms < 500:
        print 'ok'   
    else:
        convert_backend_toanoter(policy_name, working_ms)


if __name__ == '1__main__':
    while 1:
        main('apix.ruyi.ai')
        time.sleep(60)
        main('api.ruyi.ai')
        time.sleep(60)
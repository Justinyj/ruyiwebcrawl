# encoding=utf-8
import glob
import os
import sys
import json
import collections
import codecs
import re
import hashlib
import datetime
from collections import defaultdict
reload(sys)
sys.setdefaultencoding('utf-8')

sys.path.append(os.path.abspath(os.path.dirname(__file__)) )
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(__file__))))
sys.path.append(os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))



def classify_default(name):
    if len(name)<=3:
        return True

    # 莆田系特定
    if re.search(ur'(信用)',name):
        if re.search(ur'(莆田)',name):
            return False

    # 药店,美容，医药，药房
    if re.search(ur'[店市亭厅厂场厦库社处堂点吧]$',name):
        if not re.search(ur'(药店)$',name):
            return True

    #其他医院
    if re.search(ur'(动物|宠物|植物|庄稼|果蔬|兽医|蔬菜|兽药|压稼|禽|良种|农业)',name):
        return True

    #行业

    if not re.search(ur'(医院|医院.*公司|医院.*分院)$', name):
        if re.search(ur'(通信|电力|银行|邮政|邮电|建设|水利|旅游|国有|铸造|建筑|百货|服饰|门市|商场|轴承|石油|钢铁|电器|火车|购物|制盐|矿物|报业|后勤|机电|公路|建材|林业|纺织|金属|建材|农用车|电气|设计院|重工|燃气|航空|航天|能源|农产品|盐业|工程|工业|食品|烟草|电子|工贸|电业|供销|粮食|保险|交通|煤|水泥|铁通|电信|机械|汽车|葛洲坝|中信|代表处)',name):
            return True

    #服务业

    if re.search(ur'(\-|洗涤|服务|食堂|杂志|灯饰|发艺|内衣|塑料|燃料|服装|电缆|桥架|再生|石材|母婴|水产|轮胎|钢材|铺位|男装|装配|编辑部|餐饮|专业合作社|农机|客运|招待所|加油站|浴室|小卖部|报刊|停车|物业|招待|回收|维修|园林|物流|矿产|种植|足浴|冷饮|经营|代理|餐厅|舞厅|医院路|合作社|旅社|商行)',name):
        return True

    return False

def classify_invest(name):
    if re.search(ur'(莆田.*信用)', name):
        return True

    if re.search(ur'(公司)$', name):
        if re.search(ur'(投资|控股)', name):
            return True

    if re.search(ur'(集团|集团.*公司)$', name):
        if re.search(ur'(医|药|保健)', name):
            return True

    return False

def classify_medical_invests(name):
    if re.search(ur'(医院|医疗|健康).*(投资|控股)', name):
        return True

    if re.search(ur'(医院|医疗|生物).*(管理)', name):
        return True

    if re.search(ur'(医院|医疗|健康).*(集团|集团.*公司)$', name):
        return True

    return False


def classify_hospital(name):
    if u'医院' in name:
        if re.search(ur'(医院|医院.*公司|医院.*分院)$', name):
            return True

        #清远市红十字中心医院肿瘤防治中心
        if re.search( ur'医院.*(肿瘤|孕).*中心$', name):
            return True

        if re.search(ur'(医院（|医院\()', name):
            return True

    return False


def is_label_medical(label, strict=True):
    if strict:
        return label in [u'医院投资',u'医院公司']
    else:
        return label in [u'医院投资',u'医院公司',u'门诊医疗']

def classify_company_name_medical(name, strict):
    label = classify_company_name(name)
    if is_label_medical(label, strict):
        return label

def classify_company_name(name):
    LABEL_DEFAULT = ""

    if classify_default(name):
        return LABEL_DEFAULT

    #,广告,银行,信用,管理,担保
    if classify_medical_invests(name):
        return u'医院投资'

    if classify_hospital(name):
        return u'医院公司'

    if re.search(ur'([诊孕男女母婴药医疗泌尿]|健康|眼科|肿瘤|体检|康复|养老|美容|整形|护理|推拿)', name):
        return u'门诊医疗'

    return LABEL_DEFAULT


def get_item_name(item):
    for p in ['name','legal_person']:
        if p in item and item[p]:
            return item[p]


def list_item_agent_name(item, includeme=False, skip=None, exclusive=None):
    names = set()
    name = get_item_name(item)
    if name:
        names.add(name)

    for key in item.keys():
        if skip and key in skip:
            continue
        if exclusive and not key in exclusive:
            continue

        v = item[key]
        if type(v) == list:
            for xitem in v:
                xname = get_item_name(xitem)
                if xname:
                    names.update( list_item_agent_name(xitem, True) )
        elif type(v) == dict:
            names.update( list_item_agent_name(v, True) )
    return names

def is_rawitem_putian_canidate(rawitem, putian_list, min_intersection=1):
    name = rawitem['name']
    label = rawitem.get("related", classify_company_name_medical(name, False) )
    rawitem['label'] = label
    if label:
        return True


    related = set( rawitem.get("related", list_item_agent_name(rawitem,False, None ,None) ) )
    temp = related.intersection(putian_list)
    if len(temp) >= min_intersection:
        print "is_rawitem_putian_canidate", name, json.dumps(list(temp), ensure_ascii=False)
        return True

    return False

def classify_agent_type(name):
    if len(name)<=4:
        return "person"
    return "company"

def classify_agent_type2(name):
    pattern = u'公司|投资|管理|协会|商会|商行|企业|商场|研究|经营|中心|基金|服务|银行|株式会社|咨询|经纪|商店|铁路|总厂|'
    pattern += u'车行|贸易部|办公室|委员会|街道|粮食局|交易|药品|集团|塑料|模具|出版|'
    pattern += u'机械|纺织|车辆|水泥|拖拉机|化工|客车|柴油|钢厂|汽车|棉纺|乳品|'
    pattern += u'电机|轴承|仪器|齿轮|造船|加工|电器|清算|军械|军械|轴承|教具|工厂|金店|'
    pattern += u'Limited|Co.|公众股|集体股'
    if len(name)<=4:
        return "person"
    elif re.search(pattern, name):
        return 'company'
    else:
        return 'person'

def get_keywords(sentences, regex_skip_word,  limit=100 ):
    import jieba

    sentence_stream = [
        [word.strip() for word in jieba.cut(sentence) if not regex_skip_word or not re.search(regex_skip_word,word)]
        for sentence in sentences
    ]

    tf_word = collections.Counter()
    tf_word_bigram = collections.Counter()
    for sentence in sentence_stream:
        for w in sentence:
            if w:
                tf_word[w]+=1

        for bigram in [u"".join(sentence[i:i+2]).strip() for i in range(len(sentence)-1) ]:
            #if re.search(regex_use_word,bigram):
            tf_word_bigram[bigram]+=1

    map_name_tf = {}
#    for tf in [tf_char, tf_char_bigram, tf_word, tf_word_bigram]:
    for tf in [tf_word, tf_word_bigram]:
        #print json.dumps(tf.most_common(limit),  ensure_ascii=False)
        for (name, freq) in tf.most_common(limit):
            map_name_tf[name] = freq + map_name_tf.get(name,0)

    return map_name_tf

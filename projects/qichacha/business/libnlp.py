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

from core.qichacha import Qichacha

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
    if re.search(ur'(动物|宠物|植物|庄稼|果蔬|兽医)',name):
        return True

    #行业

    if not re.search(ur'(医院|医院.*公司|医院.*分院)$', name):
        if re.search(ur'(通信|电力|银行|邮政|邮电|建设|水利|旅游|国有|建筑|百货|服饰|门市|商场|轴承|石油|钢铁|电器|火车|购物|制盐|矿物|报业|后勤|机电|公路|建材|林业|纺织|金属|建材|农用车|电气|设计院|重工|燃气|航空|航天|能源|农产品|盐业|工程|工业|食品|烟草|电子|工贸|电业|供销|粮食|保险|交通|煤|水泥|铁通|电信|机械|汽车|葛洲坝|中信|代表处)',name):
            return True

    #服务业
    if re.search(ur'(\-|洗涤|服务|食堂|招待所|浴室|小卖部|报刊|停车|物业|招待|回收|维修|园林|物流|矿产|种植|足浴|冷饮|经营|代理|餐厅|舞厅|医院路|合作社|旅社|商行)',name):
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
    if re.search(ur'(医院|医疗).*(投资|控股)', name):
        return True

    if re.search(ur'(医院|医疗).*(集团|集团.*公司)$', name):
        return True

    return False


def classify_hospital(name):
    if u'医院' in name:
        if re.search(ur'(医院|医院.*公司|医院.*分院)$', name):
            return True

        #清远市红十字中心医院肿瘤防治中心
        if re.search( ur'医院.*(肿瘤|孕|管理).*中心$', name):
            return True

        if re.search(ur'(医院（|医院\()', name):
            return True

    return False



def classify_company_name(name):
    LABEL_DEFAULT = ""

    if classify_default(name):
        return LABEL_DEFAULT

    #,广告,银行,信用,管理,担保
    if classify_medical_invests(name):
        return u'医院投资'

    if classify_hospital(name):
        return u'医院公司'

    if re.search(ur'([医药诊孕男女母婴疗]|健康|肿瘤|生物|康复|养老|护理|推拿)', name):
        return u'门诊医疗'

    return LABEL_DEFAULT



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

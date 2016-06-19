#!/usr/bin/env python
# -*- coding: utf-8 -*-
import urllib
import os
import sys
import collections
import codecs
import datetime
import json
import re
import hashlib
import glob
import jieba
import codecs
from pprint import pprint
from gensim import corpora, models, similarities
import gensim


from sklearn import svm
from sklearn import cross_validation
from sklearn.svm import LinearSVC
from sklearn.linear_model import SGDClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.feature_selection import VarianceThreshold
from sklearn.feature_selection import SelectFromModel
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.preprocessing import Imputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn import datasets
from sklearn import cross_validation
from sklearn.datasets.base import Bunch
from sklearn import metrics
import pickle

gcounter = collections.Counter()


def is_question_baike(question):
    if not question:
        return False
    if re.search(ur"你|我|几点|爸爸|妈妈", question):
        if re.search(ur"你知道|我[国]",question):
            return True
        else:
            return False
    elif re.search(ur"什么|最|哪|谁|有没有|几|吗|如何|是|有多|多[少远长]|怎么?样?|啥|？",question):
        return True
    elif re.search(ur"百科|距离|历史|介绍|信息",question):
        return True
    else:
        return False


def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def getLocalFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/local/"+filename

class TopicClassifier():
    def file2items(self, filepath):
        items = []
        for filename in glob.glob(filepath):
            cat = os.path.basename(filename).replace(".human.txt","")
            lines = libfile.file2list(filename)
            for line in lines:
                item = {
                    "q": line,
                    "cat": cat
                }
                gcounter["cnt-"+cat]+=1
                #print json.dumps(item, ensure_ascii=False)
                items.append(item)
        print gcounter
        return items


    def items2sentences(self, items, cat=None):
        sentences =[]
        for item in items:
            if not cat or item['cat']==cat:
                sentences.append(item['q']+" "+item['a'])
        return sentences

    def sentences2texts(self, sentences):
        #merge phrase
        sentence_stream = [
            [word for word in jieba.cut(sentence)]
            for sentence in sentences
        ]
        bigram = Phrases(sentence_stream)

        #build dict
        stop_pattern = re.compile( u"[么]")#什么怎么多少问如果就是你们这个大约您好需要治疗检查可以出现有哪些咋办情况最近之类的话一下应该前例感觉并且东西方法设备
        texts = [
            [word for word in bigram[sent] if len(word)>1 and not word in gstopwords] #stop_pattern.search(word)]
            for sent in sentence_stream
        ]
        #pprint(texts)
        #print json.dumps(texts, ensure_ascii=False)
        return texts

    def sentences2dict(self, sentences):
        #if filename_dict and os.path.exists(filename_dict):
        #    return corpora.Dictionary.load(filename_dict)

        texts =  self.sentences2texts(sentences)
        dictionary = corpora.Dictionary(texts)
        #if filename_dict:
        #    dictionary.save(filename_dict) # store the dictionary, for future reference
        #print(dictionary)

        return dictionary


    # http://radimrehurek.com/gensim/tut1.html#from-strings-to-vectors
    def topic(self, items, topn=100):
        sentences =  self.items2sentences(items)
        texts =  self.sentences2texts(sentences)
        id2word =  self.sentences2dict(sentences)
        mm = [id2word.doc2bow(text) for text in texts]

        tfidf = models.TfidfModel(mm)

        lsi = gensim.models.lsimodel.LsiModel(corpus=mm, id2word=id2word, num_topics=10)
        topicWordProbMat = lsi.print_topics(10,  num_words=50)
        topic_words = collections.Counter()
        for topic_id, topic_text in topicWordProbMat:
            for word in re.findall(u"[\u4E00-\u9FA5]{2,10}", topic_text.replace("_","")):
                topic_words[word]+=1
        #print json.dumps(topic_words.most_common(topn), ensure_ascii=False)
        #print topicWordProbMat
        topics = [word for word, freq in topic_words.most_common(topn)]
        topics = reversed(sorted(topics))
        ret = []
        for w in topics:
            print w
            ret.append(w)

        with codecs.open(FILENAME_TEST1_FEATURES,'w',encoding='utf-8') as f:
            f.write(u"\n".join(ret))

        return ret

    def train(self, items):
        topic_words = self.topic(items)

        sentences =  self.items2sentences(items)
        texts =  self.sentences2texts(sentences)
        id2word =  self.sentences2dict(sentences)

        cats = sorted(list(set([item["cat"] for item in items])))

        test1 = Bunch()
        test1.target =  [cats.index(item['cat']) for item in items]
        test1.target_names = cats
        #print test1['target']

        test1.data = []
        for item in items:
            row = []
            for topic_word in topic_words:
                if topic_word in item["q"]:
                    row.append(1)
                else:
                    row.append(0)
            test1.data.append(row)
        #print test1['data'][0]

        #X_train = X_train_data.as_matrix()
        #y_train = y_train_data.as_matrix()

        clf = Pipeline([
                #("imputer", Imputer(missing_values='NaN', strategy="mean", axis=0)),
        #        ('feature_selection', VarianceThreshold(threshold=(.97 * (1 - .97)))),
            #    ('feature_selection', SelectKBest(chi2, k=50)),
            #    ('scaler', StandardScaler()),
        #        ('classification', svm.SVC(class_weight='balanced', cache_size=10240))])
        #        ('classification', svm.LinearSVC(class_weight='balanced'))
        #        ('classification', SGDClassifier(n_jobs=-1))
                ('classification', GradientBoostingClassifier())
            ])
        text_clf = clf.fit(test1.data, test1.target)

        #3fold
        scores = cross_validation.cross_val_score(text_clf, test1.data, test1.target, cv=3)
        print scores
        print scores.mean(), scores.std()

        #confusion
        predicted = text_clf.predict(test1.data)
        print(metrics.classification_report(test1.target, predicted, target_names=test1.target_names))

        print(metrics.confusion_matrix(test1.target, predicted))
        #predicted = text_clf.predict(docs_test)
        #metrics.confusion_matrix(test1.target, predicted)

        return text_clf




def test_is_question_baike():

    assert(is_question_baike(None)== False)

    import libfile

    filenames = [
    #    getLocalFile("baike/baike_questions_pos.txt"),
        getLocalFile("baike/baike_questions_neg.txt")
    ]
    counter = collections.Counter()
    regex_white1 = ur"你知道|我[国们]";
    regex_black = ur"你|我|喜欢";
    regex_white2 = ur"什么|最|第一|哪|谁|百科|吗|是|有|多|怎么?样?|啥|如何|距离|历史|介绍|信息|？";
    for filename in filenames:
        print "=====", filename
        lines = libfile.file2list(filename)

        for line in lines:
            if is_question_baike(line):
                actual = "_pos"
            else:
                actual = "_neg"

            if not actual in filename:
                counter["F"] += 1
                print line
            else:
                counter["T"] += 1
    print counter, "accuracy", 1 - 1.0*counter["F"]/(counter["F"]+counter["T"])


def main():
    #print sys.argv

    if len(sys.argv)<2:
        show_help()
        return

    option= sys.argv[1]

    if "test" == option:
        test_is_question_baike()
    elif "train" == option:
        file_path = getLocalFile('baike/baike_questions*')
        classfier = TopicClassifier()
        items = classfier.file2items(file_path)
        classfier.train(items)


if __name__ == "__main__":
    main()

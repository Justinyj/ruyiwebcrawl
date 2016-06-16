# encoding=utf-8
import os
import networkx as nx


def getTheFile(filename):
    return os.path.abspath(os.path.dirname(__file__)) +"/"+filename

def scale():
    filename = getTheFile('wiki-vote.txt')
    G=nx.DiGraph()
    with open(filename) as file:
        for line in file:
            if line.startswith("#"):
                continue
            head, tail = [int(x) for x in line.split()]
            for i in range(0,100):
                G.add_edge(head+1000000*i,tail+1000000*i)
    print len(G)
    pr=nx.pagerank(G,alpha=0.85, max_iter=10)
    x = 0;
    for node, value in pr.items():
        #print node, value
        x = x + value
    print(x)

def personal():
    personalization = {
        1: 0.9,
        2: 0.9,
        3: 0.0,
        4: 0.0,
        5: 0.0,
        6:0,
        7:0
    }
    G = nx.Graph()
    G.add_edge(1, 3)
    G.add_edge(2, 3)
    G.add_edge(4, 3)
    G.add_edge(4, 5)
    G.add_edge(6, 3)
    G.add_edge(6, 5)
    G.add_edge(6, 7)
    pr=nx.pagerank(G,personalization=personalization, alpha=0.85)
    for node, value in pr.items():
        print node, value

def name():
    personalization = {
        u'一': 0.9,
        u'二': 0.7,
        u'三': 0.0,
    }
    G = nx.Graph()
    G.add_edge(u'一', u'三')
    G.add_edge(u'二', u'三')

    pr=nx.pagerank(G,personalization=personalization, alpha=0.85)
    for node, value in pr.items():
        print node, value


def weight():
    personalization = {
        1: 0.9,
        2: 0.7,
        3: 0.0,
        4: 0.0,
    }
    G = nx.DiGraph()
    w1 = 1
    w2 = 100
    G.add_edge(1, 3, weight=w2)
    G.add_edge(2, 3, weight=w2)
    G.add_edge(4, 3, weight=w2)
    G.add_edge(3, 4, weight=w1)
    G.add_edge(3, 1, weight=w1)
    G.add_edge(3, 2, weight=w1)
    pr=nx.pagerank_scipy(G,personalization=personalization,  alpha=0.85)
    for node, value in pr.items():
        print node, value


scale()

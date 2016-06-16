from bottle import route, run, request, get, post, response
from datetime import datetime
import codecs
from datetime import timedelta
import logging
import sys
import os
sys.path.append(os.path.dirname(__file__))
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

@get('/search')
def search():
    #print str(request.query)

    qword = request.query['q']

    msg = {"success":True, "q":qword}
    return msg


def start2():
    run(port=9002)

def start1():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("baidu.com",80))
    ipaddress = s.getsockname()[0]
    s.close()

    logging.info(ipaddress)

    run(host=ipaddress, port=9002)
    #run(host='localhost', port=8080)


if __name__ == '__main__':
    start2()

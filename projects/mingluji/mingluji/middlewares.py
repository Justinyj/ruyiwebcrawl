from agent_list import USER_AGENT_POLL
import random


class MyMiddleWare(object):

    def process_request(self, request, spider):
        try:
            ua = random.choice(USER_AGENT_POLL)
            if ua:
                request.headers.setdefault('User-Agent', ua)
        except:
            print "failed"
print

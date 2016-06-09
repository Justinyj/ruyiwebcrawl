#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# TODO worker启动程序，检测队列的batch_id, 未必是我schedule调度的domain batch_id

from __future__ import print_function, division

from gevent import monkey; monkey.patch_all()
import gevent

from rediscluster.record import Record
from rediscluster.queues import HashQueue
from rediscluster.thinredis import ThinHash
from rediscluster.redismanager import RedisManager
from awscrawler import init_distribute_queue

class Worker(object):
    """ General worker
    """
    def __init__(self):
        pass

    def work(self):
        raise NotImplementedError('This method should implemented by subclasses')

class GetWorker(Worker):

    def __init__(self, index):
        super(GetWorker, self).__init__()
        self.index = index
        self._batch_param = {}
        self.manager = RedisManager()

        for batch_id in Record.instance().get_unfinished_batch():
            parameter = Record.instance().get_parameter(batch_id)
            total_count = Record.instance().get_total_number(batch_id)
            if total_count is None:
                continue
            self.manager.init_distributed_queue(batch_id, parameter, int(total_count))
            self._batch_param[batch_id] = parameter


    def run(self, *args, **kwargs):
        """ end, background_cleansing, status:
         None,   None,                 begin
         None,   1,                    begin cleaning
         None,   0,                    finish cleaning

         time,   0,                    begin delete
         time,   None,                 finish delete

         None,   0,                    finish cleaning then exception
        """
        for batch_id, queue_dict in self.manager.cache.iteritems():
            queue = queue_dict['queue']
            if Record.instance().is_finished(batch_id) is True:
                # this queue and queue object in distributed_queues can be
                # delete, but not needed. When run finish and
                # background_cleansing finsh, this process end.
                # BTW, worker instance will reboot every 10 minutes.
                # If another worker delete queue, I don't need to do anything.
                continue

            tasks = []
            if background is None:
                tasks.append( gevent.spawn(queue.background_cleaning) )
                tasks.append( gevent.spawn(self.work, batch_id, queue_dict, *args, **kwargs) )
            elif background == '1':
                tasks.append( gevent.spawn(self.work, batch_id queue_dict, *args, **kwargs) )

            elif background == '0':
                self.manager.delete_queue(batch_id)

            gevent.joinall(tasks)


    def work(self, batch_id, queue_dict, *args, **kwargs):
        batch_key_filename = batch_id.rsplit('-', 1)[0].replace('-', '_')
        module = __import__('workers.{}'.format(batch_key_filename), fromlist=['process'])

        while 1:
            results = queue_dict['queue'].get(block=True, timeout=3, interval=1)
            if results == []: break
            for url_id, count in results:
                url = queue_dict['thinhash'].hget(url_id)

                process_status = module.process(url,
                                                self._batch_param[batch_id],
                                                *args,
                                                **kwargs)
                if process_status:
                    queue_dict['queue'].task_done(url_id)
                else:
                    Record.instance().increase_failed(batch_id)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Call Worker with arguments')
    parser.add_argument('--index', '-i', type=int, help='index of this machine in all this batch machines')
    parser.add_argument('--cookie', '-c', type=str, help='cookie for this machine')
    option = parser.parse_args()
    if option.index:
        obj = GetWorker(option.index)
        if option.cookie:
            obj.run(cookie=option.cookie)
        else:
            obj.run()

if __name__ == '__main__':
    main()


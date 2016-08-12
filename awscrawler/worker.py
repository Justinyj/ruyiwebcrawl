#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
# TODO worker启动程序，检测队列的batch_id, 未必是我schedule调度的domain batch_id

from __future__ import print_function, division

import time

from rediscluster.record import Record
from rediscluster.redismanager import RedisManager
from settings import RECORD_REDIS, QUEUE_REDIS, CACHE_REDIS

from crawlerlog.cachelog import get_logger
from datetime import datetime


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
        self.process_time = {}
        self.manager = RedisManager(RECORD_REDIS, QUEUE_REDIS, CACHE_REDIS)

        for batch_id in Record.instance().get_unfinished_batch():
            parameter = Record.instance().get_parameter(batch_id)
            total_count = Record.instance().get_total_number(batch_id)
            if total_count is None:
                continue
            self.manager.worker_init_distributed_queue(batch_id, int(total_count))
            self._batch_param[batch_id] = parameter
            self.process_time[batch_id] = 0, 0

    def schedule(self, *args, **kwargs):
        """ I believe the third time sleep 4 minutes, all the queues will be fill enough data.
            And all timehash in queue will be back to queue.
            We can change the parameter whenever needed.
        """
        timeout = time_to_sleep = kwargs.get('timeout', 60)

        while 1:
            self.run(*args, **kwargs)
            time.sleep(10)

        for i in range(4):
            self.run(*args, **kwargs)
            time.sleep(time_to_sleep)
            time_to_sleep = timeout * 2 ** i

    def run(self, *args, **kwargs):
        """ end, background_cleansing, status:
         None,   None,                 begin
         None,   1,                    begin cleaning
         None,   0,                    finish cleaning

         time,   0,                    begin delete
         time,   None,                 finish delete

         None,   0,                    finish cleaning then exception
        """
        checkout_cache = {}
        for batch_id, queue_dict in self.manager.get_queue_with_priority():
            queue = queue_dict['queue']
            if Record.instance().is_finished(batch_id) is True:
                # this queue and queue object in distributed_queues can be
                # delete, but not needed. When run finish and
                # background_cleansing finsh, this process end.
                # BTW, worker instance will reboot every 10 minutes.
                # If another worker delete queue, I don't need to do anything.
                continue

            background = queue.get_background_cleaning_status()

            if background == '0':
                pass
            elif background is None or background == '1':
                checkout_cache[batch_id] = queue_dict


        today_str = datetime.now().strftime('%Y%m%d')
        while len(checkout_cache) > 0:
            removes = []
            batch_urlid = {}

            for batch_id, queue_dict in checkout_cache.iteritems(): # get url_ids from queue
                get_logger(batch_id, today_str, '/opt/service/log/').info('begin get items from queue')
                results = queue_dict['queue'].get(block=True, timeout=3, interval=1)
                get_logger(batch_id, today_str, '/opt/service/log/').info('finish get items from queue')

                if not results:
                    removes.append(batch_id)
                    continue
                batch_urlid[batch_id] = results
            [checkout_cache.pop(i) for i in removes]
            doing_queues = batch_urlid.keys()

            while len(doing_queues) > 0:
                for batch_id, results in batch_urlid.iteritems(): # download and process
                    if len(results) > 0:
                        url_id = results.pop()
                        other_batch_process_time = self.get_other_batch_process_time( set(doing_queues) - set([batch_id]) )
                        start = time.time()

                        self.work(batch_id, checkout_cache[batch_id], url_id, other_batch_process_time, *args, **kwargs)
                        self.update_process_time_of_this_batch(batch_id, start)
                    else:
                        doing_queues.remove(batch_id)


    def work(self, batch_id, queue_dict, url_id, other_batch_process_time, *args, **kwargs):
        try:
            batch_key_filename = batch_id.rsplit('-', 1)[0].replace('-', '_')
            module = __import__('workers.{}'.format(batch_key_filename), fromlist=['process'])
        except:
            module = __import__('workers.prefetch', fromlist=['process'])

        if kwargs and kwargs.get("debug"):
            get_logger(batch_id, today_str, '/opt/service/log/').info('begin get url from thinhash redis')

        # TODO change to hmget
        url = queue_dict['thinhash'].hget(url_id)

        if kwargs and kwargs.get("debug"):
            get_logger(batch_id, today_str, '/opt/service/log/').info('end get url from thinhash redis')

        try:
            process_status = module.process(url,
                                            batch_id,
                                            self._batch_param[batch_id],
                                            self.manager,
                                            other_batch_process_time,
                                            *args,
                                            **kwargs)
        except Exception as e:
            Record.instance().add_exception(batch_id, url, repr(e))
            queue_dict['queue'].task_done(url_id)
            continue

        if process_status:
            if kwargs and kwargs.get("debug"):
                get_logger(batch_id, today_str, '/opt/service/log/').info('begin task done for record redis')

            queue_dict['queue'].task_done(url_id)
            Record.instance().increase_success(batch_id)

            if kwargs and kwargs.get("debug"):
                get_logger(batch_id, today_str, '/opt/service/log/').info('end task done for record redis')


    def get_other_batch_process_time(self, other_batches):
        """ For every batch, everage process time is duration divideed by times,
            add all the average process time
        """
        other_batch_process_time = 0

        for batch in other_batches:
            duration, times = self.process_time[batch]
            other_batch_process_time += (0 if times == 0 else duration / times)
        return other_batch_process_time


    def update_process_time_of_this_batch(self, batch_id, start):
        duration = time.time() - start
        total_duration, times = self.process_time[batch_id]
        self.process_time[batch_id] = total_duration + duration, times + 1


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Call Worker with arguments')
    parser.add_argument('--index', '-i', type=int, help='index of this machine in all this batch machines')
    parser.add_argument('--cookie', '-c', type=str, help='cookie for this machine')
    parser.add_argument('--timeout', '-t', type=float, default=60, help='timeout for timehash to enqueue')
    parser.add_argument('--debug', '-d', type=bool, default=True, help='print debug info')
    option = parser.parse_args()
    if option.index:
        obj = GetWorker(option.index)
        if option.cookie:
            obj.schedule(cookie=option.cookie, timeout=option.timeout, debug=option.debug)
        else:
            obj.schedule(timeout=option.timeout, debug=option.debug)

if __name__ == '__main__':
    main()

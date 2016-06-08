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

        self.queues = [i for i in self._get_task_queue()]
        self.distributed_queues = [] # distributed init at scheduler end,
                                     # not worker end

        for q in self.queues:
            parameter = Record.instance().get_parameter(q.key)
            total_count = Record.instance().get_total_number(q.key)
            if total_count is None:
                self.distributed_queues.append(None)
                continue
            obj = init_distribute_queue(q.key, parameter, int(total_count))
            self.distributed_queues.append(obj)


    def _get_task_queue(self):
        keys = Record.instance().get_unfinished_batch()
        for key in keys:
            yield HashQueue(key, priority=2, timeout=90, failure_times=3)

    def _check_empty_queue(self, queue):
        """ after 3 times of get, result is empty
        """
        for i in range(3):
            results = queue.get(block=True, timeout=3, interval=1)
            if results != []:
                return False
        return True

    def delete_queue_check(self, queue):
        ret = self._check_empty_queue(queue)
        if ret is False:
            return False
        ret = Record.instance().is_finished(queue.key)
        if ret is True:
            return False
        status = queue.get_background_cleaning_status()
        if status != '0':
            return False
        return True

    def run(self, *args, **kwargs):
        """ end, background_cleansing, status:
            0,   None,                 begin
            0,   1,                    begin cleansing
            0,   0,                    finish cleansing
         time,   0,                    begin delete
         time,   None,                 finish delete
            0,   0,                    finish cleansing with exception
        """
        for idx, queue in enumerate(self.queues):
            background = queue.get_background_cleaning_status()
            if Record.instance().is_finished(queue.key) is True:
                # this queue and queue object in distributed_queues can be
                # delete, but not needed. When run finish and
                # background_cleansing finsh, this process end.
                # BTW, worker instance will reboot every 10 minutes.
                # If another worker delete queue, I don't need to do anything.
                continue

            tasks = []
            queue_dict = self.distributed_queues[idx]
            if background is None:
                tasks.append( gevent.spawn(queue.background_cleaning) )
                tasks.append( gevent.spawn(self.work, queue_dict, *args, **kwargs) )
            elif background == '1':
                tasks.append( gevent.spawn(self.work, queue_dict, *args, **kwargs) )

            elif background == '0':
                ret = self.delete_queue_check(queue)
                if ret is True:
                    # caution! atom operation
                    try:
                        Record.instance().end(queue.key)
                        queue_dict['thinhash'].delete()
                        queue.flush()
                    except:
                        Record.instance().from_end_rollback(queue.key)

            gevent.joinall(tasks)


    def work(self, queue_dict, *args, **kwargs):
        if not hasattr(self, '_batch_param'):
            setattr(self, '_batch_param', {})

        batch_id = queue_dict['queue'].key
        param = self._batch_param.get(batch_id)
        if param is None:
            parameter = Record.instance().get_parameter(batch_id)
            self._batch_param[batch_id] = parameter

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


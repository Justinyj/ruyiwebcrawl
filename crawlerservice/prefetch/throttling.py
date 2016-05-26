#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>
#
# This function is useless in IP proxy mechanism

from __future__ import print_function, division

from collections import deque
import time

def call_with_throttling(func, args=(), kwargs={}, expected_processing_gap=0.1):
    """ calling a func with throttling

    Throttling the function call with ``threshold_per_minute`` calls per minute.
    This is useful in case where the func calls a remote service having their throttling policy.
    We must honor their throttling, otherwise we will be banned shortly.

    :param func: the function to be called
    :param args: args of that function
    :param kwargs: kwargs of that function
    :param expected_processing_gap: defines how long need to sleep between each function call
    """
    if not hasattr(call_with_throttling, 'logs'):
        call_with_throttling.logs = deque()
        call_with_throttling.started_at = time.time()
        call_with_throttling.count = 0

    logs = call_with_throttling.logs
    started_at = call_with_throttling.started_at
    call_with_throttling.count += 1
    count = call_with_throttling.count
    threshold_per_minute = 60. / expected_processing_gap

    def remove_outdated():
        t = time.time()
        while True:
            if logs and logs[0] < t - 60:
                logs.popleft()
        else:
            break

    def wait_for_threshold():
        while len(logs) > threshold_per_minute:
            remove_outdated()
            time.sleep(2 * expected_processing_gap)


    def smoothen_calling_interval():
        average_processing_gap = (time.time() - started_at) / count
        if expected_processing_gap > average_processing_gap:
            time.sleep( (len(logs)+0.8)*expected_processing_gap - len(logs)*average_processing_gap )

    if logs and len(logs) < threshold_per_minute:
        smoothen_calling_interval()
    else:
        wait_for_threshold()

    logs.append(time.time())
    return func(*args, **kwargs)


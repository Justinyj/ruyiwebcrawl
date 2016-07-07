#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

from gevent import monkey; monkey.patch_all()
from gevent import signal
import gevent
import time


def add_func(x):
  x += 2
  time.sleep(0.5)
  print('add result: ', x)
  return x


def patch_greenlet(func):
  """ Slove:
      "Impossible to call blocking function in the event loop callback"

      New problem:
      this wrapper function is called after global gevent.joinall.
      I can use gevent.pool.Pool() to spawn in this function and join globally.
      But here I user [do_sth(t.value) for t in tasks] in the last of this program.

  """
  def inner(*args, **kwargs):
      return gevent.spawn(func, *args, **kwargs)
  return inner


@patch_greenlet
def callback(green):
  """ add sleep here, make it blocking function.
      error: "Impossible to call blocking function in the event loop callback"
  """
  time.sleep(3)
  y = green.value
  print('callback: ', y)

def callback_v2(green):
  time.sleep(3)
  y = green.value
  print('callback: ', y)

def blocking_callback():
   """ return:
   time python gevent_callback_blocking.py
   before join
   add result:  5
   callback:  5
   add result:  4
   after join
   python gevent_callback_blocking.py  0.05s user 0.02s system 1% cpu 5.581 total
   """
   tasks = []
   t1 = gevent.spawn_later(0, add_func, 3)
   t1.rawlink(callback)
   tasks.append(t1)

   t2 = gevent.spawn_later(5, add_func, 2)
   t2.rawlink(callback)
   tasks.append(t2)


   print('before join')
   gevent.joinall(tasks)
   print('after join')


def blocking_callback_v2():
   tasks = []
   t1 = gevent.spawn_later(0, add_func, 3)
   tasks.append(t1)

   t2 = gevent.spawn_later(10, add_func, 2)
   tasks.append(t2)


   print('before join')
   gevent.joinall(tasks)
   print('after join')

   for t in tasks:
       callback_v2(t)

def signal_handler(*_):
    print('signal catch', _)

def catch_signal():
    signal.signal(2, signal_handler)
    signal.signal(15, signal_handler)

catch_signal()
blocking_callback_v2()

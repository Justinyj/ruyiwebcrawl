#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yixuan Zhao <johnsonqrr (at) gmail.com>

from movedata import DataMover

import os
import importlib
import argparse
import sys
reload(sys)

def main():
    parser = argparse.ArgumentParser(description='just for batchid argument, maybe more in future')
    parser.add_argument('--batchid', '-b', type=str, help='the batch_id of spider and loader such as kmzydaily')
    batch_id = parser.parse_args().batchid
    if batch_id:
        mover = DataMover(batch_id=batch_id)
        move_success = mover.run()
        if move_success:
            loader_module_name = '{}_loader'.format('kmzydaily')
            loader_module = __import__(loader_module_name, fromlist=['process'])
            loader_class_name = '{}Loader'.format('kmzydaily'.capitalize())
            loader_class = getattr(loader_module, loader_class_name)

            obj = loader_class()
            obj.read_jsn(mover.dir_path)
        else:
            # slack? log? retry?
            pass


if __name__ == '__main__':
    main()

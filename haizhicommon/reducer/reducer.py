#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Yuande Liu <miraclecome (at) gmail.com>

from __future__ import print_function, division

import marshal
import zlib
import base64


def action(cmd, index, machine_num):
    exec(marshal.loads(zlib.decompress(base64.b64decode(cmd))), {'index': index, 'machine_num': machine_num}, {})


def parse_arg():
    import argparse
    parser = argparse.ArgumentParser(prog='python reducer.py',
                                     description='react commond from server.',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--program', '-p', type=str, help='program to execute')
    parser.add_argument('--index', '-i', type=int, help='number of this machine')
    parser.add_argument('--machine_num', '-m', type=int, help='number of all machines')
    return parser.parse_args(), parser


def main():
    args, parser = parse_arg()

    try:
        if not args.program:
            raise()
        action(args.program, args.index, args.machine_num)
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(e)
        parser.print_help()


if __name__ == '__main__':
    main()


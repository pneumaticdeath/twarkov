#!/usr/bin/python

# Copyright 2009, 2020, Mitch Patenaude

import argparse
import sys
import users

from chain_utils import *

if __name__ == "__main__":
  
    parser = argparse.ArgumentParser('update.py')
    parser.add_argument('--continuous', '-c', action='store_true', help='Update continuously')
    parser.add_argument('--user', '-u', default='sharon', help='Which user to update')
    args = parser.parse_args()

    try:
        user = users.load(args.user)
        if args.continuous:
            continuous_update(user)
        else:
            check_updates(user)
    except ValueError as e:
        sys.stderr.write('{}\n'.format(str(e)))



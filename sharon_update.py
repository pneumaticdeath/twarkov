#!/usr/bin/python

# Copyright 2009, Mitch Patenaude

import sys
import users

from chain_utils import *

if __name__ == "__main__":
  # TODO(mitch): replace ghetto argument parsing
  sharon = users.load('sharon')
  if len(sys.argv) > 1 and sys.argv[1] == '-c':
    continuous_update(sharon.chain)
  else:
    do_all(sharon.chain)



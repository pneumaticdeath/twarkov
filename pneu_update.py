#!/usr/bin/python

# Copyright 2009, Mitch Patenaude

import sys
from users import pneu

from chain_utils import *

if __name__ == "__main__":
  # TODO(mitch): replace ghetto argument parsing
  if len(sys.argv) > 1 and sys.argv[1] == '-c':
   continuous_update(pneu.chain)
  else:
    do_all(pneu.chain)



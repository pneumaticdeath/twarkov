#!/usr/bin/python

# Copyright 2009, Mitch Patenaude

import sys
import users

from chain_utils import *

if __name__ == "__main__":
  # TODO(mitch): replace ghetto argument parsing
  pneu = users.load('pneumaticdeath')
  if len(sys.argv) > 1 and sys.argv[1] == '-c':
    continuous_update(pneu)
  else:
    check_updates(pneu)



#!/usr/bin/python


from twarkov import CharChain, TwarkovChain
# from exp_twarkov import CharChain, TwarkovChain
# from chain_utils import candidate_words.

import getopt
import random
import sys
import time
import tweetdb
from markov.limited_types import simple_set as set

# DEBUG = True
DEBUG = False

# DEFAULT_DEPTH=13
DEFAULT_DEPTH=4

# FIXME(mitch): This should be auto generated.
_words = ["This ", "I ", "Just ", "My ", "The ", "I'm ", "It's ", "If ", "At ",
          "New ", "In ", "Thanks ", "Good ", "A ", "You ", "Question ", "It ",
          "We ", "About ", "Big ", "Had ", "Not ", "People ", "Thank ",
          "Things ", "Today ", "Very ", "Dear ", "Great ", "Hey, ", "No ",
          "Off ", "Oh, ", "Taking ", "That ", "Happy ", "Having ", "Heading ",
          "Looking ", "One ", "There ", "Well, ", "To ", "Why ", "How ",
          "Okay, ", "Blog ", "Going ", "Watching ", "What ", "I've ",
          "On ", "And ", "For ", "Is ", "So ", "Oh ",
          ]

def babble(chain, count=200, depth=None, attribution=False):
  msg_cnt = 0
  ls = set()
  # hackish heuristic to mix up depths, but favor longer chains
  # depths = [chain._max,]
  #for i in xrange(1,chain._max-chain._min):
  #  depths += range(chain._min+i,chain._max+1)
  # if DEBUG: print depths
  if depth is not None:
    d = depth;
  else:
    d = chain._max

  while msg_cnt < count:
    # d = random.choice(depths)
    # word = random.choice(_words)
    word = None
    ls.clear()
    try:
      msg = chain.GetMessage(word, depth=d, labelset=ls)
      msg = filter(lambda x: x != '\n' and x != '\r',msg)
      # chk_len = int(0.75*len(msg))
      if len(ls) > 1:
          # and not chain._tweetstore.matching(msg[:chk_len], ignore_case=True) 
          # and not chain._tweetstore.matching(msg[-chk_len:], ignore_case=True)):
        if attribution:
          authors = list(set([tw.user.screen_name for tw in [chain._tweetstore[i] for i in ls]]))
          if len(authors) > 1:
            authorstr = ' h/t to @%s and @%s' % (', @'.join(authors[:-1]), authors[-1])
          else:
            authorstr = ' h/t to @' + authors[0]
        else:
          authorstr = '';
        print "%s (%d)%s" % (msg.encode('utf-8'),len(ls), authorstr.encode('utf-8'))
        msg_cnt += 1
        # time.sleep(5)
      elif DEBUG:
        print "REJECTED: %2d: %s" % (d, msg,)
    except UnicodeEncodeError:
      pass

def usage():
  sys.stderr.write('%s [-d] [-C] [-a] [-c count] [-m max_depth] tweetdb\n' % (sys.argv[0]))

if __name__ == '__main__':
  count = 0
  max_tuple = None
  charchain = False
  attribution = False

  try:
    opts, args = getopt.getopt(sys.argv[1:], 'dCac:m:')

    for opt,value in opts:
      if opt == '-d':
        DEBUG=True
      elif opt == '-c':
        count = int(value)
      elif opt == '-m':
        max_tuple = int(value)
      elif opt == '-C':
        charchain = True
      elif opt == '-a':
        attribution = True
      else:
        sys.stderr.write('Unknown option %d\n' % (opt,))
        usage()
        sys.exit(1)
  except getopt.GetoptError, e:
    sys.stderr.write('%d\n' % (str(e),))
    usage()
    sys.exit(1)

  if not args:
    sys.stderr.write('Please specify a tweet database\n')
    usage()
    sys.exit(1)

  if max_tuple is None:
    if charchain:
      max_tuple = 14
    else:
      max_tuple = 4

  if charchain:
    chain = CharChain(max=max_tuple, storefile=args[0])
  else:
    chain = TwarkovChain(max=max_tuple, storefile=args[0])

  if count:
    babble(chain, count, attribution=attribution)
  else:
    babble(chain, attribution=attribution)



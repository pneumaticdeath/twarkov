#!/usr/bin/python


from twarkov import CharChain, TwarkovChain
# from exp_twarkov import CharChain, TwarkovChain
# from chain_utils import candidate_words.

import getopt
import json
import logging
import os
import random
import sys
import time
import tweetdb
from markov.limited_types import simple_set as set
from markov.tree import MarkovChain
from markov.prefix_sql import MarkovPrefixSql

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

def babble_json(chain, count=1):
  messages = []
  for x in range(count):

    msg = chain.GetAnnotatedMessage(max_len=1024)
    while reject_annotated(msg):
      # logging.info('Rejected "{}"'.format(msg['message'].encode('utf-8')))
      msg = chain.GetAnnotatedMessage(max_len=1024)

    messages.append(msg)

  return json.dumps(messages, indent=2)

def reject_annotated(msg):
  # reject messages from a single tweet
  if len(msg["tweets"]) <= 1:
    logging.debug('Rejected "{}" because it\'s based on a single tweet.'.format(msg['message'].encode('utf-8')))
    return True

  # reject messages from a single author
  authorset = set()
  for tw in msg["tweets"].values():
    authorset.add(tw["username"])

  if len(authorset) <= 1:
    logging.debug('Rejected "{}" becasue it\'s based on a single author\'s tweets'.format(msg['message'].encode('utf-8')))
    return True

  # reject tweets where 80% or more can be made from a single tweet
  tweet_symbol_count = {}
  for element in msg["sequence"]:
    for tw_id in element['labels']:
      if tw_id in tweet_symbol_count:
        tweet_symbol_count[tw_id] += 1
      else:
        tweet_symbol_count[tw_id] = 1
  threshold = len(msg["sequence"]) * 0.8
  for tw_id, count in tweet_symbol_count.items():
    if count >= threshold:
      logging.debug('Rejecting "{}" because 80% or more is derived from tweet_id {}'.format(msg['message'].encode('utf-8'), tw_id))
      return True

  return False

def usage():
  sys.stderr.write('%s [-d] [-C] [-j] [-s] [-a] [-c count] [-m max_depth] tweetdb\n' % (sys.argv[0]))

if __name__ == '__main__':
  count = 1
  max_tuple = None
  charchain = False
  attribution = False
  dump_json = False
  sql_prefix_store = False

  try:
    opts, args = getopt.getopt(sys.argv[1:], 'dCjsac:m:')

    for opt,value in opts:
      if opt == '-d':
        DEBUG=True
      elif opt == '-c':
        count = int(value)
      elif opt == '-m':
        max_tuple = int(value)
      elif opt == '-C':
        charchain = True
      elif opt == '-j':
        dump_json = True
      elif opt == '-a':
        attribution = True
      elif opt == '-s':
        sql_prefix_store = True
      else:
        sys.stderr.write('Unknown option %d\n' % (opt,))
        usage()
        sys.exit(1)
  except getopt.GetoptError as e:
    sys.stderr.write('{}\n'.format(e))
    usage()
    sys.exit(1)

  if DEBUG:
    logging.basicConfig(level=logging.DEBUG)
  else:
    logging.basicConfig(level=logging.INFO)

  if not args:
    sys.stderr.write('Please specify a tweet database\n')
    usage()
    sys.exit(1)

  if max_tuple is None:
    if charchain:
      max_tuple = 14
    else:
      max_tuple = 4

  kwargs = {'max': max_tuple, 'storefile': args[0]}
  if sql_prefix_store:
    base_store = '.'.join(os.path.basename(args[0]).split('.')[:-1])
    kwargs['dbfile'] = 'chains/{}_{}{}.sqlite'.format(base_store, 'char' if charchain else 'word', max_tuple)
    kwargs['chain_factory'] = MarkovPrefixSql
    kwargs['seperator'] = '' if charchain else ' '

  logging.debug('kwargs for chain are {}'.format(repr( kwargs)))

  if charchain:
    logging.debug('Creating character chain of length {}'.format(max_tuple))
    chain = CharChain(**kwargs)
  else:
    logging.debug('Creating word chain of legnth {}'.format(max_tuple))
    chain = TwarkovChain(**kwargs)

  logging.debug('Chain created')

  if dump_json:
    print(babble_json(chain, count))
  else:
    babble(chain, count=count, attribution=attribution)

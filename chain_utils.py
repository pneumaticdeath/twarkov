#!/usr/bin/python

# Copyright 2009, Mitch Patenaude

import os
import random
import time
import urllib2
from markov.limited_types import simple_set
from tweetdb import textof


def check_updates(chain):
  fr_tweets = chain.GetApi().GetHomeTimeline()
  new_tweets = filter(lambda t: t not in chain._tweetstore and t not in chain._rejectstore, fr_tweets)
  unfamiliar = filter(lambda t: not chain.isFamiliar(t), new_tweets)
  print "%d new tweets from friends found, and %d were used" % (
     len(new_tweets), chain.UpdateFromStatuses(new_tweets))
  if unfamiliar:
    print "These tweets looked unfamiliar:"
    print_tweets(unfamiliar)

def print_tweets(tweetset):
  for t in tweetset:
    print " %15s: %s" % (t.user.screen_name, textof(t))

def print_stats(chain):
  print "Total word count %d with %d distinct words" % (chain.count, len(chain))

def candidate_words(chain, word_count=40, triple_count=25):
  """Return a good list of candidate words"""

  words = filter(lambda x: (x[0].isupper() or x[0] == '@') 
                           and chain[x].count >= word_count 
                           and sum([len(y) for y in chain[x].values()]) >= triple_count,
                 chain.keys())
  if len(words) > 3:
    return words
  else:
    # Hail Mary play, just return all uppercase words that lead somewhere
    return filter(lambda x: x[0].isupper() and len(chain[x]) > 0, chain.keys())

def print_candidate_tweet(chain):
  # words = candidate_words(chain)
  words = []
  ls = simple_set()
  if words and len(words) > 3:
    wotd = random.choice(candidate_words(chain))
    print "The word of the day is \"%s\"." % wotd
  else:
    print "Insufficient candidate words, going random"
    wotd = None
  for d in xrange(chain._max, max(chain._min-1,chain._max-5,1), -1):
    ls.clear()
    msg = chain.GetMessage(wotd, max_len=300, depth=d, labelset=ls)
    print "%d-tuple message (using %d tweets):" % (d, len(ls))
    print msg
    source_tweets = 0
    for tw_id in ls:
      tw = chain._tweetstore[tw_id]
      print "  %s: %s" % (tw.user.screen_name, textof(tw))
      source_tweets += 1
      if source_tweets >= 10:
          print "  <and so on....>"
          break

def print_candidate_tweets(chain, depth=None, words=None):
  ls = simple_set()
  if words is None:
    words = candidate_words(chain)
  print 'Candidate words: "%s" & "%s"' % ('", "'.join(words[:-1]),words[-1])
  if depth:
    print "Generating %d-tuples" % depth
  for word in words:
    ls.clear()
    print chain.GetMessage(word, depth=depth, max_len=300, labelset=ls)
    for tw_id in ls:
      tw = chain._tweetstore[tw_id]
      print "  %s: %s" % (tw.user.screen_name, textof(tw))

def do_all(chain):
  check_updates(chain)
  print_stats(chain)
  print_candidate_tweet(chain)

def continuous_update(chain, normal_sleep_time=600, fail_sleep_time=600, error_sleep_time=900):
  err_count = 0
  try:
    while True:
      try:
        do_all(chain)
        chain._tweetstore.sync()
        sleep_time=normal_sleep_time
        err_count = 0
      except urllib2.HTTPError as e:
        err_count += 1
        print "%s: Got a Fail Whale(sleeping for %d): %s " % (time.asctime(), fail_sleep_time, e)
        sleep_time=fail_sleep_time
      except KeyboardInterrupt as e:
        raise e
      except IOError, e:
        err_count += 1
        print "%s: got %s exception type: %s" \
               % (time.asctime(), e.__class__.__name__, e)
        sleep_time=error_sleep_time
      except ValueError as e:
        err_count += 1
        if err_count > 5:
          raise e
        else:
          sleep_time=error_sleep_time*err_count
          print "%s: JSON error?, sleeping for %d: %s " % (time.asctime(), sleep_time, e)
      print "%s: Sleeping for %d minutes (%d seconds)" \
            % (time.asctime(), (sleep_time+30)/60, sleep_time)
      time.sleep(sleep_time)
      print "\n"
  except KeyboardInterrupt:
    print "Goodbye!"


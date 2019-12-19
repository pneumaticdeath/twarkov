#!/usr/bin/python

# Copyright 2009-2019 Mitch Patenaude

import time
import urllib2
from twarkov import follow_retweets
from tweetdb import textof


def check_updates(user):
  fr_tweets = user.api.GetHomeTimeline()
  fr_tweets = [follow_retweets(t) for t in fr_tweets]
  new_tweets = filter(lambda t: t not in user.chain._tweetstore and t not in user.chain._rejectstore, fr_tweets)
  unfamiliar = filter(lambda t: not user.chain.isFamiliar(t), new_tweets)
  print "%d tweets received, %d new tweets from friends found, and %d were used" % (
     len(fr_tweets), len(new_tweets), user.chain.UpdateFromStatuses(new_tweets))
  print_tweets(new_tweets)
  if unfamiliar:
    print "These tweets looked unfamiliar:"
    print_tweets(unfamiliar)

def print_tweets(tweetset):
  for t in tweetset:
    print " %15s: %s" % (t.user.screen_name, textof(t))

def continuous_update(user, normal_sleep_time=600, fail_sleep_time=600, error_sleep_time=900):
  err_count = 0
  try:
    while True:
      try:
        check_updates(user)
        user.chain._tweetstore.sync()
        sleep_time=normal_sleep_time
        err_count = 0
      except urllib2.HTTPError as e:
        err_count += 1
        print "%s: Got a Fail Whale(sleeping for %d): %s " % (time.asctime(), fail_sleep_time, e)
        sleep_time=fail_sleep_time
      except KeyboardInterrupt as e:
        raise e
      except Exception as e:
        err_count += 1
        print("{}: got {} exception type: {}".format(time.asctime(), e.__class__.__name__, e))
        if err_count > 5:
          raise e
        else:
          sleep_time=error_sleep_time*err_count
      print "%s: Sleeping for %d minutes (%d seconds)" \
            % (time.asctime(), (sleep_time+30)/60, sleep_time)
      time.sleep(sleep_time)
      print "\n"
  except KeyboardInterrupt:
    print "Goodbye!"

#!/usr/bin/env python

# Copyright 2011, Mitch Patenaude

__author__ = "Mitch Patenaude <patenaude@gmail.com>"

import random
from tweetdb import TweetStore

class TwarkovPrefixChain(object):
  """A Markov Chain character babbler for twitter

  This implementation uses character prefixes of length m for each
  n-tuple character chain, where m<n, and it typically between n/2 
  and n/3."""

  DEFAULT_TWEETSTORE_FILE = 'tweetstore'

  def __init__(self, api=None, storefile=DEFAULT_TWEETSTORE_FILE,
               autopopulate=True, max=12, prefix=4, max_auto=None):
    self._api = api
    self._storefilename = storefile
    self.max = max
    self.prefix = prefix
    self.tweetcount = 0
    self._tweetstore = TweetStore(storefile)
    self._prefixmap = dict()
    self._tweetmap = dict()

    if self._storefilename and autopopulate:
      tweet_count=0
      try:
        for tw in self._tweetstore.values():
          self._ProcTweet(tw)
          tweet_count += 1
          # print "Proced tw# %d: %s" % (tweet_count, tw.text)
          if max_auto is not None and tweet_count >= max_auto:
            break
      except KeyboardInterrupt:
        pass

  def _ProcTweet(self, tweet):
    # print "Processing tweet %d: %s" % (tweet.id, tweet.text)
    text = tweet.text
    tweet_id = tweet.id
    self._tweetmap[tweet_id] = text
    length = len(text)
    index = 0
    while index < length-self.max:
      key = text[index:index+self.prefix]
      if key not in self._prefixmap:
        self._prefixmap[key] = list()
      self._prefixmap[key].append(TweetTuple(tweet_id, index))
      index += 1

  def GetMessage(self, seed=None, max_len=140, tweet_stack=None):
    if seed is None:
      tweet_id,tweet_text = random.choice(self._tweetmap.items())
      seed = tweet_text[0:self.max]
      if tweet_stack is not None:
        tweet_stack.append(TweetTuple(tweet_id,0))
        last_tweet_id = tweet_id

    if len(seed) < self.max:
      tupleSet = self._GetTupleSetMatching(seed)
      x = random.choice(tupleSet)
      seed = self._tweetmap[x.tweet_id][x.index:x.index+self.max]
      if tweet_stack is not None:
        tweet_stack.append(x)
        last_tweet_id = x.tweet_id

    if len(seed) < self.max:
      return seed

    output = seed
    while len(output) < max_len:
      seed=output[-self.max:]
      tupleSet = self._GetTupleSetMatching(seed)
      if not tupleSet:
        break
      choice = random.choice(tupleSet)
      if tweet_stack is not None and choice.tweet_id != last_tweet_id:
        tweet_stack.append(choice)
        last_tweet_id = choice.tweet_id
      tweet_text = self._tweetmap[choice.tweet_id]
      char = tweet_text[choice.index+self.max]
      if not char:
        return output
      output += char

    return output

  def _GetTupleSetMatching(self, seed):
    key = seed[:self.prefix]
    matchSet = list()
    if key not in self._prefixmap:
      return None
    for tup in self._prefixmap[key]:
      tweet_text = self._tweetmap[tup.tweet_id]
      if seed == tweet_text[tup.index:tup.index+len(seed)]:
        matchSet.append(tup)
    return matchSet

  def DumpTweetStack(self, tuple_stack):
    for tt in tuple_stack:
      print self._tweetmap[tt.tweet_id]
      print '%s^%s^' % (' '*tt.index,'-'*(self.max-2))



class TweetTuple(object):
  __slots__ = ('tweet_id','index')
  def __init__(self, tweet_id, index):
    self.tweet_id = tweet_id
    self.index = index

  def __str__(self):
    return 'TweetTuple(%d,%d)' % (self.tweet_id,self.index)


#!/usr/bin/python

# Copyright 2009, Mitch Patenaude

__author__ = "Mitch Patenaude (patenaude@gmail.com)"

from markov.tree import MarkovChain 
import twitter
from tweetdb import TweetStore, TweetStoreSQL, textof

class ApiMissing(Exception): 
  """Raised when there is no default Api instnace, and none is specified in the arguments"""
  pass 

class TwarkovChain(MarkovChain):

  """A MarkovChain based word babbler for twitter.

  Does an n-tuple (up to the specified max tuple size) word
  frequency analysis.  It can then generate messages that
  conform to that n-tuple frequency distribution.

  Arguments: (all optional)
    api: The twitter.Api instance used by default.
    max: Maximum tuple size to consider. Values larger than 4 can chew up a
      lot of memory.
    storefile: The dbm (BerkeleyDB) file where already processed tweets
      should be stored.  If None, then an in-memory store will be used.
    autopopulate: Set to False if you don't want the current chain to be
      populated from the backstore.  Makes initialization faster if you 
      are only doing updates and not twittering.
    familiar: If set, then it will provide a threshold for which tweets to
      process, so that crust like tweets in other languages or random
      gibberish from creeping in.  If set to a floating value between 0.0
      and 1.0 (exclusive), then at least that proportion of words in the 
      tweet must have been seen to be considered.  If a positive integer,
      then at least that number of words in the tweet must have been 
      seen, or all the words in the total # of words in the tweet is 
      smaller than that.
  """

  DEFAULT_TWEETSTORE_FILE = 'tweetstore'

  # This is a marker for the beginning of a chain. It should not exist in
  # the regular input domain.
  _begin_marker = ' '

  def __init__(self,api=None, 
               storefile=DEFAULT_TWEETSTORE_FILE,
               autopopulate=True, familiar=None, rejectfile=None, **kwargs):

    MarkovChain.__init__(self, **kwargs)
    self._api=api
    self._familiar=familiar
    self.tweetcount = 0
    if storefile and '.sqlite' in storefile:
      self._tweetstore = TweetStoreSQL(storefile)
    else:
      self._tweetstore = TweetStore(storefile)
    self._rejectstore = TweetStore(rejectfile)

    #populate the chain from the tweetstore
    if self._tweetstore and autopopulate:
      for tw in self._tweetstore.values():
        #override the default familiarity theshold, since tweets in the
        #store are considered to be pre-approved, and besides, if the 
        #chain is empty, then nothing will reach a non-zero threshold
        # 0 is used because None is the guard value.
        self._ProcTweet(tw, familiar=0)

  def GetApi(self):
    """Returns the default API handler, or raises an exception if missing"""
    if self._api is None:
      raise ApiMissing("No default api specified")
    return self._api

  def SetApi(self, api):
    """Sets the default twitter.Api instance to use for this chain"""
    self._api = api

  def UpdateFromPublic(self,api=None):
    """Updates from the Public timeline.

    Arguments:
      api: The #twitter.Api object to use for the update (or default)

    Returns:
      count of the previously unseen tweets processed.

    Raises:
      ApiMissing: if there isn't a default API and none is specified
    """
       
    if api is None:
      api = self.GetApi()
    return self.UpdateFromStatuses(api.GetPublicTimeline())

  def UpdateFromUser(self, user, count=50, api=None):
    if api is None:
      api = self.GetApi()
    return self.UpdateFromStatuses(api.GetUserTimeline(user=user, count=count))

  def UpdateFromFriends(self,api=None):
    """Update the chain from the Friends timline.

    Update the chain statistics from the recent tweets of friends using the
    api specified, or the default otherwise. The api should be authenicated
    as a real user.

    Arguments:
      api: [optional] the twitter.Api instance to use

    Returns: an integer representing the number of new tweets processed

    Raises:
      ApiMissing: if no api is specified and there isn't a default
    """
    if api is None:
      api = self.GetApi()
    return self.UpdateFromStatuses(api.GetFriendsTimeline())

  def UpdateFromStatuses(self,statuses):
    tweet_count = 0
    for tweet in statuses:
      while hasattr(tweet, 'retweeted_status'):
        tweet = tweet.retweeted_status
      if tweet not in self._tweetstore:
        if self._ProcTweet(tweet) > 0:
          self._tweetstore.add(tweet)
          tweet_count += 1
        else:
          self._rejectstore.add(tweet)
    return tweet_count

  def _ProcTweet(self, tweet, familiar=None):
    words = self._Tokenize(textof(tweet))
    if self.isFamiliar(tweet, familiar, words):
      # we use a beginning of sequence marker, it should not exist in the
      # regular input domain
      words = [self.__class__._begin_marker, ] + list(words)
      self.Update(words, label=tweet.id)
      return 1
    else:
      return 0

  def _Tokenize(self,text):
    """Tokenizing method, can be overridden in subclasses"""
    return text.split()

  def isFamiliar(self, tweet, familiar=None, words=None):
    if familiar is None and self._familiar is not None:
      familiar = self._familiar

    if familiar:

      if words is None:
        words = self._Tokenize(textof(tweet))

      wordcount = len(words)
      matchcount = len(filter(lambda w: w in self, words))

      if familiar < 1:
        # assume a floating point threshold
        return (1.0*matchcount)/wordcount >= familiar
      else:
        return matchcount >= min(familiar,wordcount)
    else:
      return True # no familiarity threshold

  def GetMessage(self, seed=None, max_len=280,
                 depth=None, sep=" ", trunc_char=None, labelset=None):
    """Get a random message.

    Returns a text message of a maximum length, based on the optional seed phrase.

    Arguments:
      seed: [optional] phrase to use to seed the message.  
      max_len: The maximum length of the message, which will be
        truncated at the last truc_char within the limit.
      depth: The depth in the tree to use for statistics
        default is the maximum tuple size.
      sep: separator string to use between words in the message.
      trunc_char: The character used to truncate messags that are
        too long. Defaults to the separator character.
      

    Returns:
      A string with the message.  It will be a null string if the seed does not
      exist in the chain.
    """
    if trunc_char is None:
      trunc_char = sep

    seed_seq = None
    if seed is not None:
      seed_seq = tuple(self._Tokenize(seed))
    else:
      seed_seq = self.GetRandomTuple((self.__class__._begin_marker,),labelset=labelset)[1:]

    try:
      gen = self.GetRandomSequence(seed=seed_seq, depth=depth, labelset=labelset)
    except KeyError:
      return ''

    try:
      msg = ''
      msg = gen.next()
      while len(msg) < max_len:
        msg += sep + gen.next()
      # if we fell through, msg might be too long
      if len(msg) > max_len:
        # Need to look starting at max_len+1 becuase there might
        # be a seperator there, and if so, that's the one we want.
        rightmost_trunc_pos = msg.rfind(trunc_char, 0, max_len+1)
        if rightmost_trunc_pos > 0:
          msg = msg[0:rightmost_trunc_pos]
        else:
          msg = msg[0:max_len]
    except StopIteration:
      pass
    return msg

  def GetAnnotatedMessage(self, seed=None, max_len=280, depth=None, sep=' ', trunc_char=None):
    if depth is None:
      depth = self._max

    retval = {'seperator': sep, 'depth': depth, 'seed': seed}

    if seed:
      seed_seq = self._Tokenize(seed)
    else:
      seed_seq = self.GetRandomTuple((self.__class__._begin_marker,))[1:]

    try:
      gen = self.GetAnnotatedSequence(seed=seed_seq, depth=depth)

      retseq = []
      length = 0
      sep_length = len(sep)
      position = 0
      trunc_position = 0
      all_labels = set()
      for element, labels in gen:
        element_length = len(element)
        if max_len-length < element_length:
          retseq = retseq[:trunc_position]
          break
        length += element_length + sep_length
        if trunc_char is None or element.endswith(trunc_char):
          trunc_position = position
        all_labels |= labels
        retseq.append((element, [str(l) for l in labels]))
        position += 1

      retval['sequence'] = [dict(element=e, labels=l) for e, l in retseq]
      retval['message'] = sep.join([x[0] for x in retseq])
      tweets = {}
      for i in all_labels:
        tw = self._tweetstore[i]
        tweets[str(i)] = dict(text=textof(tw), username=tw.user.screen_name)
      retval['tweets'] = tweets

    except KeyError as e:
      retval['error'] = str(e)

    return retval

class CharChain(TwarkovChain):
  # a two character string shouldn't be in the input domain, since we normally only deal in single characters.
  _begin_marker = '--'

  def _Tokenize(self, text):
    return text

  def GetMessage(self, seed=None, max_len=280,
                 depth=None, sep='', trunc_char=" ", labelset=None):
    return TwarkovChain.GetMessage(self, seed, max_len, depth, sep, trunc_char, labelset)

  def GetAnnotatedMessage(self, seed=None, max_len=280,
                          depth=None, sep='', trunc_char=' '):
    return TwarkovChain.GetAnnotatedMessage(self, seed, max_len, depth, sep, trunc_char)

if __name__ == "__main__":
  tc = TwarkovChain()
  # api = twitter.Api()
  # tc.UpdateFromPublic(api)
  print tc.GetMessage()


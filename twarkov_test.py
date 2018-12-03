#!/usr/bin/python

# Copyright 2009, Mitch Patenaude

import unittest
import twarkov

class _MockTweet:
  def __init__(self, id=None, text=None, user=None):
    self.id = id
    self.text = text
    self.user = user

class _MockUser:
  def __init__(self, id=None, name=None, screen_name=None):
    self.id = id
    self.name = name
    self.screen_name = screen_name

class TwarkovMessageTests(unittest.TestCase):
  def setUp(self):
    tc = twarkov.TwarkovChain(max=2,storefile=None)
    tc._UpdateTuple(('xx','yy'))
    tc._UpdateTuple(('yy','xx'))
    tc._UpdateTuple(('foobar','xx'))
    self.tc = tc

  def testMessageRepeatingLength(self):
    msg = self.tc.GetMessage("xx", max_len=9)
    self.assertEqual(msg, 'xx yy xx', "Got \"%s\" not expected string" % msg)

  def testNoExtraSeparator(self):
    msg = self.tc.GetMessage("xx", max_len=6)
    self.assertEqual(msg, 'xx yy', "Got \"%s\" not expected string" % msg)

  def testLengthExact(self):
    msg = self.tc.GetMessage("xx", max_len=5)
    self.assertEqual(msg, 'xx yy', "Got \"%s\" not expected string" % msg)

  def testMidwordTruncationFallback(self):
    msg = self.tc.GetMessage('foobar',max_len=5)
    self.assertEqual(msg, 'fooba', "Didn't trucate, got \"%s\"" % msg)

  def tearDown(self):
    del self.tc

class TwarkovFamiliarityTests(unittest.TestCase):

  def setUp(self):

    self.origtweet = _MockTweet(id = 1,
      text = "This is a long text string that should have lots of words")
    # 12 words, all unique, but the last one won't appear in the chain
    # because the last tuple to be processed, so "words" wouldn't be 
    # counted. so this won't match fully, but 11 should match.

    self.similartweet = _MockTweet(id = 2,
      text = "Now this is a similar text string with a few similar words")
    # 12 words, 6 in original, but only 5 should match since 
    # "This" != "this" If future implementations smash case or 
    # all words in the original end up inside , then 6 will match

    self.shorttweet = _MockTweet(id = 3, text="This is a text string")
    # 5 words, all match

    self.gibberishtweet = _MockTweet(id = 4,
      text = "tHiSs TWWeet iIS ENtiREly DISsimILAR")
    # Shouldn't match, even if you smashcase.

    self.tc = twarkov.TwarkovChain(max=3, storefile=None, familiar=0.25)
    # if the override doesn't work, then they all fail
    self.tc._ProcTweet(self.origtweet,familiar=0)

  def assertIsSimilar(self, tweet, familiar, text=None):
    self.assertTrue(self.tc.isFamiliar(tweet, familiar), text)

  def assertNotSimilar(self, tweet, familiar, text=None):
    self.assertFalse(self.tc.isFamiliar(tweet, familiar), text)

  def testOrigTextAtDefault(self):
    self.assertIsSimilar(self.origtweet, None, 
         "original tweet isn't familiar at default threshold.")

  def testOrigTextAtHighThreshold(self):
    self.assertNotSimilar(self.origtweet, 0.99, 
         "original tweet isn't familiar at high threshold.")

  def testOrigTextAtLowIntegerThreshold(self):
    self.assertIsSimilar(self.origtweet, 3,
         "original tweet should be familiar at 3")

  def testOrigTextAtHighIntegerThreshold(self):
    self.assertIsSimilar(self.origtweet, 11,
         "original tweet should be familiar at 11")

  def testOrigTextAtMaxIntegerThreshold(self):
    self.assertNotSimilar(self.origtweet, 100,
         "original tweet should not be recognized at 100.")

  def testShortTextAtDefaultThreshold(self):
    self.assertIsSimilar(self.shorttweet, None,
         "short tweet should have all words recognized.")

  def testShortTextAtLowThreshold(self):
    self.assertIsSimilar(self.shorttweet, 0.1,
         "short tweet should have all words recognized.")

  def testShortTextAtHighThreshold(self):
    self.assertIsSimilar(self.shorttweet, 0.99,
         "short tweet should have all words recognized.")

  def testShortTextAtLowIntegerThreshold(self):
    self.assertIsSimilar(self.shorttweet, 1,
         "short tweet should have all words recognized.")

  def testShortTextAtHighIntegerThreshold(self):
    self.assertIsSimilar(self.shorttweet, 5,
         "short tweet should have all words recognized.")

  def testShortTextAtMaxIntegerThreshold(self):
    self.assertIsSimilar(self.shorttweet, 100,
         "short tweet should have all words recognized.")

  def testSimilarTextAtDefaultThreshold(self):
    self.assertIsSimilar(self.similartweet, None,
         "similar tweet not recognized at default")

  def testSimilarTextAtHalfThreshold(self):
    self.assertNotSimilar(self.similartweet, 0.5,
         "similar tweet should not have been recognized at 0.5")

  def testSimilarTextAtLowIntegerThreshold(self):
    # See disccussion in the setUp() section as to why this 
    # should match at 5.
    self.assertIsSimilar(self.similartweet, 5,
         "similar tweet should have been recognized at 2")
    
  def testSimilarTextAtHighIntegerThreshold(self):
    self.assertNotSimilar(self.similartweet, 6,
         "similar tweet incorrectly recognized at 6")

  def testGibberishTweetAtDefaultThreshold(self):
    self.assertNotSimilar(self.gibberishtweet, None,
         "gibberish tweet incorrectly recognized at default")
  
  def testGibberishTweetAtLowIntegerThreshold(self):
    self.assertNotSimilar(self.gibberishtweet, 1,
         "gibberish tweet incorrectly recognized at 1")
  
  def testGibberishTweetAtLowFloatingThreshold(self):
    self.assertNotSimilar(self.gibberishtweet, 0.05,
         "gibberish tweet incorrectly recognized at 0.05")

  def testGibberishTweetWithOverride(self):
    self.assertIsSimilar(self.gibberishtweet, 0,
         "gibberish tweet should have been recognized with override")

if __name__ == "__main__":
  unittest.main() 

#!/usr/bin/python

import anydbm
import cPickle
import logging
import sqlite3
import twitter

def textof(tweet):
    if hasattr(tweet,'full_text') and len(tweet.full_text) > 0:
        return tweet.full_text
    else:
        return tweet.text

class TweetStore(object):
  """A persistent store for all tweets (twitter.Status) messages"""

  def __init__(self,filename=None):
    if filename:
      self._in_memory=False
      self._store = anydbm.open(filename,'c')
    else:
      self._in_memory=True
      self._store = {}

  def __del__(self):
    self.close()

  def __itoa(self,int_id):
    return "%d" % int_id

  def __atoi(self,str_id): return int(str_id) 
  def __setitem__(self,key,value):
    self._store[self.__itoa(key)]=cPickle.dumps(value)

  def __getitem__(self,key):
    return cPickle.loads(self._store[self.__itoa(key)])

  def __delitem__(self,key):
    del self._store[self.__itoa(key)]

  def __contains__(self,key):
    if type(key) is twitter.Status:
      return self.__itoa(key.id) in self
    if type(key) is int:
      return self.__itoa(key) in self
    else:
      return key in self._store

  def keys(self):
    return [self.__atoi(keystr) for keystr in self._store.keys()]

  def values(self):
    return [cPickle.loads(valstr) for valstr in self._store.values()]

  def items(self):
    return [(self.__atoi(keystr),cPickle.loads(valstr)) for (keystr,valstr) in self._store.items()]

  def close(self):
    if not self._in_memory:
      self._store.close()

  def add(self,status):
    self[status.id] = status

  def matching(self,substr, ignore_case=False):
    """return tweets having text containing that substring."""
    if ignore_case: 
      filterfunc = lambda x: substr.lower() in textof(x).lower()
    else:
      filterfunc = lambda x: substr in textof(x)

    return filter(filterfunc, self.values())

  def sync(self):
    if self._in_memory:
      self._store.sync()
    else:
      # nothing to do for an in-memory store
      pass

class TweetStoreSQL(object):
    class PseudoTweet(object):
        class PseudoUser(object):
            def __init__(self, username):
                self.screen_name = username

        def __init__(self, result):
            tweet_id, tweet, username = result
            self.id = tweet_id
            self.text = tweet
            self.user = self.PseudoUser(username)

    def __init__(self, filename=None):
        self.filename = filename
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect(self.filename)
        self.cur = self.conn.cursor()
        self.cur.execute('PRAGMA journal_mode=wal')
        self.cur.execute('''CREATE TABLE IF NOT EXISTS tweets(
            tweet_id INT,
            tweet TEXT,
            username TEXT,
            PRIMARY KEY (tweet_id) ON CONFLICT IGNORE
        ) WITHOUT ROWID;''')

    def __del__(self):
        self.sync()
    
    def __setitem__(self, key, value):
        try:
            self.cur.execute("""INSERT INTO tweets(tweet_id, tweet, username) 
                VALUES(?, ?, ?);""", (key, textof(value), value.user.screen_name))
        except sqlite3.OperationalError as e:
            logging.error('Unable to add tweet to {}: {}'
                           .format(self.filename, str(e)))


    def __getitem__(self, key):
        results = self.cur.execute("""SELECT tweet_id, tweet, username
            FROM tweets WHERE tweet_ID = ?;""", (key,))
        for r in results:
            return self.PseudoTweet(r)

    def __delitem__(self, key):
        try:
            self.cur.execute("""DELETE FROM tweets WHERE tweet_id = ?;""", 
                    (key,))
        except sqlite3.OperationalsError as e:
            logging.error('Unable to delete key {} in {}: {}'
                    .format(key, self.filename, str(e)))

    def __contains__(self, key):
        if type(key) is twitter.Status or type(key) is self.PseudoTweet:
            return key.id in self
        else:
            results = self.cur.execute("""SELECT COUNT(*) FROM tweets
                WHERE tweet_id = ?;""", (key,));
            for r in results:
                return r[0] >= 1;

    def keys(self):
        results = self.cur.execute("""SELECT tweet_id FROM tweets;""")
        return [r[0] for r in results]

    def values(self):
        results = self.cur.execute("""SELECT tweet_id, tweet, username
            FROM tweets;""")
        return [self.PseudoTweet(r) for r in results]

    def items(self):
        return [(t.id, t) for t in self.values()]

    def close(self):
        self.sync()

    def add(self, tweet):
        self[tweet.id] = tweet

    def matching(self, substr, ignore_case=False):
        if ignore_case:
            filterfunc = lambda x: substr.lower() in textof(x).lower()
        else:
            filterfunc = lambda x: substr in textof(x)

        return filter(filterfunc, self.values())

    def sync(self):
        self.conn.commit()


if __name__ == "__main__":

  import sys
  import codecs

  if len(sys.argv) > 1:
    dbfile = sys.argv[1]
    ts = TweetStore(dbfile)
    if len(sys.argv) > 2:
      # outfile = codecs.open(sys.argv[2],'w','utf-8')
      outfile = open(sys.argv[2],'wb')
    else:
      # this proved entirely ineffective.  
      # outfile = codecs.EncodedFile(sys.stdout, 'utf-8', file_encoding='ascii',errors='ignore')
      outfile = sys.stdout
      
    for tw in ts.values():
      text = filter(lambda x: x != '\n', textof(tw))
      outfile.write(('%10d %20s: %s\n' % (tw.id, tw.user.screen_name, text)).encode('utf-8'))
    outfile.close()
    ts.close()
  else:
    sys.stderr.write('usage: %s <tweetdb_file> [<output_file>]\n' % sys.argv[0])
    sys.exit(1)


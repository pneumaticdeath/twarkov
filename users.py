#!/usr/bin/env python

import json
import os
import twitter
import twarkov
import tweetdb


CONFIG_PATH = '~/.twarkov'

class User(object):
    def __init__(self, config):
        self._config = config
        self._api = None
        self._chain = None
        self._store = None

    @property
    def api(self):
        if self._api is None:
            self._api = twitter.Api(**self._config['twitter'])
        return self._api

    @property
    def chain(self):
        if self._chain is None:
            self._chain = twarkov.TwarkovChain(api=self.api, **self._config['chain'])
        return self._chain

    @property
    def tweetstore(self):
        if self._store is None:
            if '.sqlite' in self._config['tweetstore']:
                self._store = tweetdb.TweetStoreSQL(self._config['tweetstore'])
            else:
                self._store = tweetdb.TweetStore(self._config['tweetstore'])
        return self._store

def load(username):
    configfile = os.path.join(CONFIG_PATH, 'users.json')
    conf = json.loads(open(os.path.expanduser(configfile), 'r').read())
    if username not in conf:
        raise ValueError('Can\'t find user "{}"'.format(username))

    return User(conf[username])

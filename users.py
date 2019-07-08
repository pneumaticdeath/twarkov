#!/usr/bin/env python

import config
import json
import os
import twitter
import twarkov
import tweetdb


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
            self._store = tweetdb.TweetStore(self._config['tweetstore'])
        return self._store

def load(username):
    conf = config.get_json('users.json')
    if username not in conf:
        raise ValueError('Can\'t find user "{}"'.format(username))

    return User(conf[username])

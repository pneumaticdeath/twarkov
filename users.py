#!/usr/bin/env python

import json
import os
import twitter
import twarkov


CONFIG_PATH = '~/.twarkov'

class User(object):
    def __init__(self, config):
        self._config = config
        self._api = None
        self._chain = None

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

def load(username):
    configfile = os.path.join(CONFIG_PATH, 'users.json')
    conf = json.loads(open(os.path.expanduser(configfile), 'r').read())
    if username not in conf:
        raise ValueError('Can\'t find user "{}"'.format(username))

    return User(conf[username])

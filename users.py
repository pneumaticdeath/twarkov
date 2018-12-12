#!/usr/bin/env python

import json
import os
import twitter
import twarkov


CONFIG_PATH = '~/.twarkov'

class User(object):
    def __init__(self, api, **kwargs):
        self.api = api
        self.chain = twarkov.TwarkovChain(api=api, **kwargs)

def load(username):
    configfile = os.path.join(CONFIG_PATH, 'users.json')
    conf = json.loads(open(os.path.expanduser(configfile), 'r').read())
    if username not in conf:
        raise ValueError('Can\'t find user "{}"'.format(username))

    twitter_api = twitter.Api(**conf[username]['twitter'])
    return User(api=twitter_api, **conf[username]['chain'])

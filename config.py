#!/usr/bin/env python

import json
import os


CONFIG_DIR = '~/.twarkov'

def get_path(config_file):
    newpath = os.path.join(os.path.expanduser(CONFIG_DIR), config_file)
    try:
        os.makedirs(os.path.dirname(newpath), mode=0700)
    except OSError as e:
        if 'exists' not in str(e):
            raise e
    return newpath

def get_file(config_file, mode='r'):
    return open(get_path(config_file), mode)

def get_json(config_file):
    return json.loads(get_file(config_file).read())

#!/usr/bin/env python

import json
import os


CONFIG_DIR = '~/.twarkov'

def get_path(config_file):
    return os.path.join(os.path.expanduser(CONFIG_DIR), config_file)

def get_file(config_file, mode='r'):
    return open(get_path(config_file), mode)

def get_json(config_file):
    return json.loads(get_file(config_file).read())

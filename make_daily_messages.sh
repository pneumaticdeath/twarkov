#!/bin/bash

echo "15 character chains:"
time ./babble.py -s -d -C -m 15 -c 20 -j stores/sharon.sqlite > html/char15.json

echo "4 word chains:"
time ./babble.py -s -d -m 4 -c 20 -j stores/sharon.sqlite > html/word4.json

echo "3 word chains:"
time ./babble.py -s -d -m 3 -c 20 -j stores/sharon.sqlite > html/word3.json


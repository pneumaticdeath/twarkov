#!/bin/bash

echo "20 character chains:"
time ./babble.py -s -d -C -m 20 -c 20 -j stores/sharon.sqlite > html/char20.json

echo "18 character chains:"
time ./babble.py -s -d -C -m 18 -c 20 -j stores/sharon.sqlite > html/char18.json

# echo "15 character chains:"
# time ./babble.py -s -d -C -m 15 -c 20 -j stores/sharon.sqlite > html/char15.json

echo "4 word chains:"
time ./babble.py -s -d -m 4 -c 20 -j stores/sharon.sqlite > html/word4.json

# echo "3 word chains:"
# time ./babble.py -s -d -m 3 -c 20 -j stores/sharon.sqlite > html/word3.json

echo "Syncing to website"
rsync -av html/* patenaude@sharonmarkov.net:sharonmarkov.net/twarkov/.

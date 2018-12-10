echo "14 character chains:"
time ./babble.py -d -C -m 14 -c 20 -j stores/sharon.sqlite > html/char14.json

echo "8 character chains:"
time ./babble.py -d -C -m 8 -c 20 -j stores/sharon.sqlite > html/char8.json

echo "4 word chains:"
time ./babble.py -d -m 4 -c 20 -j stores/sharon.sqlite > html/word4.json

echo "3 word chains:"
time ./babble.py -d -m 3 -c 20 -j stores/sharon.sqlite > html/word3.json


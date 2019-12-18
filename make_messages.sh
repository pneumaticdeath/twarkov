#!/bin/bash

export PYTHONPATH=/home/mitch/pylib
cd $(dirname $0)
ds=$(date +%Y-%m-%d-%H%M)
archivedir=json_archive
htmldir=html

echo "20 character chains:"
time ./babble.py -s -d -C -m 20 -c 5 -j stores/sharon.sqlite > ${archivedir}/char20-${ds}.json
ln -f ${archivedir}/char20-${ds}.json ${htmldir}/char20.json

echo "18 character chains:"
time ./babble.py -s -d -C -m 18 -c 5 -j stores/sharon.sqlite > ${archivedir}/char18-${ds}.json
ln -f ${archivedir}/char18-${ds}.json ${htmldir}/char18.json

echo "4 word chains:"
time ./babble.py -s -d -m 4 -c 10 -j stores/sharon.sqlite > ${archivedir}/word4-${ds}.json
ln -f ${archivedir}/word4-${ds}.json ${htmldir}/word4.json

./sync.sh

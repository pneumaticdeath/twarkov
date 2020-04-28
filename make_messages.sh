#!/bin/bash

export PYTHONPATH=/home/mitch/pylib
cd $(dirname $0)
user=sharon
ds=$(date +%Y-%m-%d-%H%M)
archivedir=~/.twarkov/generated/${user}/json_archive
htmldir=~/.twarkov/generated/${user}/html

echo "$(date): 20 character chains:"
time ./babble.py -s -d -C -m 20 -c 5 -j stores/${user}.sqlite > ${archivedir}/char20-${ds}.json
ln -f ${archivedir}/char20-${ds}.json ${htmldir}/char20.json

echo "$(date): 18 character chains:"
time ./babble.py -s -d -C -m 18 -c 5 -j stores/${user}.sqlite > ${archivedir}/char18-${ds}.json
ln -f ${archivedir}/char18-${ds}.json ${htmldir}/char18.json

echo "$(date): 4 word chains:"
time ./babble.py -s -d -m 4 -c 10 -j stores/${user}.sqlite > ${archivedir}/word4-${ds}.json
ln -f ${archivedir}/word4-${ds}.json ${htmldir}/word4.json

echo "$(date): 5 word chains:"
time ./babble.py -s -d -m 5 -c 10 -j stores/${user}.sqlite > ${archivedir}/word5-${ds}.json
ln -f ${archivedir}/word5-${ds}.json ${htmldir}/word5.json

./sync.sh

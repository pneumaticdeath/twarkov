#!/bin/bash
cd $(dirname $0)
echo "Syncing to website"
rsync -av html/* patenaude@sharonmarkov.net:sharonmarkov.net/twarkov/.

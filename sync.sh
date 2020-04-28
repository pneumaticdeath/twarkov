#!/bin/bash
cd $(dirname $0)
user=sharon
echo "Syncing ${user} to website"
rsync -av ~/.twarkov/generated/${user}/html/* patenaude@sharonmarkov.net:sharonmarkov.net/twarkov/.

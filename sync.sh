#!/bin/bash
echo "Syncing to website"
rsync -av html/* patenaude@sharonmarkov.net:sharonmarkov.net/twarkov/.

#!/bin/bash

#defaulrts
user='sharon' 
interval=60

while getopts ":u:i:" opt; do
  case ${opt} in
    u )
      user="${OPTARG}"
      ;;
    i )
      interval="${OPTARG}"
      ;;
    \? )
      echo "chain_monitor.sh [-u user] [-i interval] chainspec [chainspec ...] " 1>&2
      exit 1
      ;;
    : )
      echo "argument ${OPTARG} requires an argument" 1>&2
      exit 1
  esac
done

shift $((OPTIND -1))

if [[ $# -lt 1 ]]; then
  echo "chain_monitor.sh [-u user] [-i interval] chainspec [chainspec ...] " 1>&2
  exit 1
fi

dbfile=~/.twarkov/stores/"${user}".sqlite
for chainspec in "$@"
do 
  chainfile=~/.twarkov/chains/"${user}"_"${chainspec}".sqlite
  total=$(echo 'select count(*) from tweets;' | sqlite3 "${dbfile}")
  done=$(echo 'select count(*) from seen_labels;' | sqlite3 "${chainfile}")
  last=$(( $total - $done ))
  echo $(basename ${chainfile}) $(date) ${total} ${last}
  while sleep $interval
  do
    done=$(echo 'select count(*) from seen_labels;' | sqlite3 "${chainfile}")
    # total=$(echo 'select count(*) from tweets;' | sqlite3 "${dbfile}")
    current=$(( $total - $done ))
    if [[ $current -eq $last ]]; then
      echo $(basename "${chainfile}") $(date) ${current} $(( $last - $current )) DONE
      break
    else 
      echo $(basename "${chainfile}") $(date) ${current} $(( $last - $current )) $(date -d "now + $(echo "( $interval * $current / ( $last - $current ) )" | bc -l) seconds")
    fi
    if [[ $current -le 0 ]]
    then
      break
    fi 
    last=$current
  done
  echo done with $(basename ${chainfile})
  sleep 600
done

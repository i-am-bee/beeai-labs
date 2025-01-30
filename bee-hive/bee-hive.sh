#!/bin/sh

cmd=${CONTAINER_CMD:-docker}
if [ "$1" != "build" ] && [ "$1" != "run" ]; then
    echo "Invalid argument. Must be 'build' or 'run'."
    exit 1
fi

if [ "$1" == "build" ]; then
    $cmd build -t bee-hive .
elif [ "$1" == "run" ]; then
    echo "Running..."
    path=$2
    agents=$3
    workflow=$4
    env=""
    while [ "$5" != "" ]; do
        env=$env" -e "$5" "
        shift
    done
    $cmd run  $env --mount type=bind,src=$path,target=/data bee-hive /data/$agents /data/$workflow
fi




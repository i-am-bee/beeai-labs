#!/bin/sh

cmd=${CONTAINER_CMD:-docker}
target=${TARGET_IP:-127.0.0.1:5000}
if [ "$1" != "build" ] && [ "$1" != "deploy" ] && [ "$1" != "run" ]; then
    echo "Invalid argument. Must be 'build', 'deploy' or 'run'."
    exit 1
fi

if [ "$1" == "build" ]; then
    echo "Building..."
    $cmd build -t bee-hive .
elif [ "$1" == "deploy" ]; then
    echo "Deploying..."
    env=""
    while [ "$2" != "" ]; do
        env=$env" -e "$2" "
        shift
    done
    $cmd run  -d $env -p $target:5000 bee-hive
elif [ "$1" == "run" ]; then
    echo "Running..."
    agents=$2
    workflow=$3
    curl -X POST -L http://$target/ -F "agents=@$agents" -F "workflow=@$workflow"
fi




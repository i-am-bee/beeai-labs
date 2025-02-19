#!/bin/sh

cmd=${CONTAINER_CMD:-docker}
target=${TARGET_IP:-127.0.0.1:5000}
flags=${BUILD_FLAGS}
if [ "$1" != "build" ] && [ "$1" != "deploy" ]&& [ "$1" != "deploy-k" ] && [ "$1" != "run" ]; then
    echo "Invalid argument. Must be 'build', 'deploy' or 'run'."
    exit 1
fi

if [ "$1" == "build" ]; then
    echo "Building..."
    $cmd build $flags -t maestro -f Dockerfile ..
elif [ "$1" == "deploy" ]; then
    echo "Deploying..."
    env=""
    while [ "$2" != "" ]; do
        env=$env" -e "$2" "
        shift
    done
    $cmd run  -d $env -p $target:5000 maestro
elif [ "$1" == "deploy-k" ]; then
    echo "Deploying (kubernetes)..."
    cp maestro.yaml temp-maestro.yaml
    while [ "$2" != "" ]; do
        keyvalue=$2
	name=$(echo $keyvalue | cut -d= -f1)
        value=$(echo $keyvalue | cut -d= -f2)
        sed  -i -e "s#env:#env:\n        - name: $name\n          value: $value#" temp-maestro.yaml
        shift
    done
    kubectl apply -f temp-maestro.yaml
elif [ "$1" == "run" ]; then
    echo "Running..."
    agents=$2
    workflow=$3
    curl -s -X POST -L http://$target/ -F "agents=@$agents" -F "workflow=@$workflow" | awk '{gsub(/\\n/,"\n")}1'

fi

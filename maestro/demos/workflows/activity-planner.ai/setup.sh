#! /bin/bash
cp example.env .env
cp .env ./../common/src
cd ../../../bee-hive
poetry env activate
poetry install
cd -
./../common/src/create_agents.py ./agents.yaml

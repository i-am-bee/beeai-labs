#! /bin/bash
cp example.env .env
cp .env ./../common/src
cd ../../../maestro
poetry env activate
poetry install
cd -
./../common/src/create_agents.py ./agents.yaml

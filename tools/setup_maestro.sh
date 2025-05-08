#!/usr/bin/env bash
#
# Usage:
#   source ./tools/setup_maestro.sh (from root level)
#
# This will:
#   1) Install all Poetry deps
#   2) Install extras from requirements.txt without deps
#   3) Drop you into the Poetry venv shell

# 1) Lock & install Poetry deps
poetry lock
poetry install

VENV_PATH=$(poetry env info --path)
source "$VENV_PATH/bin/activate"

pip install crewai litellm==1.67.0.post1 # bypass crewai dependency issue
# Weather-Checker Example

A multi-agent workflow using Bee-Hive to check if the current temperature in a location is hotter or colder than average.

## Getting Started

* Run a local instance of the Bee Stack

* Install dependencies: `pip install -r ../../bee-hive/requirements.txt`

* Configure environmental variables: `cp example.env .env`

* Copy `.env` to main bee-hive directory: `cp .env ../../bee-hive`

* Create the agents: `./hive create agents.yaml`

* Open the UI ( http://localhost:3000 ) and enable the `OpenMateo` tool for both agents

* Run the workflow: `./hive run workflow.yaml` (to run for a different city, change the `prompt` field in `workflow.yaml`)

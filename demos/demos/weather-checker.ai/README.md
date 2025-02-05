# Weather-Checker Example

A multi-agent workflow using Bee-Hive to check if the current temperature in a location is hotter or colder than average.

## Getting Started

* Run a local instance of the [bee-stack](https://github.com/i-am-bee/bee-stack/blob/main/README.md)

* Install [bee-hive](https://github.com/i-am-bee/bee-hive) dependencies: `cd ../../../../bee-hive/bee-hive && poetry shell && poetry install && cd -`

* Configure environmental variables: `cp example.env .env`

* Copy `.env` to main bee-hive directory: `cp .env ../../../../bee-hive/bee_hive`

* Create the agents: `./hive create agents.yaml`

* Run the workflow: `./hive run workflow.yaml` (to run for a different city, change the `prompt` field in `workflow.yaml`)

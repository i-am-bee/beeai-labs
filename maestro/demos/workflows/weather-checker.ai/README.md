# Weather-Checker Example

A multi-agent workflow using Maestro to check if the current temperature in a location is hotter or colder than average.

## Getting Started

* Run a local instance of the [bee-stack](https://github.com/i-am-bee/bee-stack/blob/main/README.md)

* Verify a valid llm is available to bee-stack

* Install [maestro](https://github.com/i-am-bee/beeai-labs) dependencies: `cd ../../../maestro && poetry shell && poetry install && cd -`

* Configure environmental variables: `cp example.env .env`

* Copy `.env` to common directory: `cp .env ./../common/src`

## Running workflow

Assuming you are in maestro level:

Create the agents (and enable the tools): `maestro create ./demos/workflows/weather-checker.ai/agents.yaml`

To run the workflow:

If you already created the agents and enabled the tool: `maestro run None ./demos/workflows/weather-checker.ai/workflow.yaml`

OR

Directly run the workflow: `maestro run ./demos/workflows/weather-checker.ai/agents.yaml ./demos/workflows/weather-checker.ai/workflow.yaml`

If in the actual weather demo directory, you can also directly run using: `./run.sh`.
(To run for a different city, change the `prompt` field in `workflow.yaml`)

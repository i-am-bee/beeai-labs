# Weather-Checker Example

A multi-agent workflow using Maestro to check if the current temperature in a location is hotter or colder than average.

## Mermaid Diagram

<!-- MERMAID_START -->
```mermaid
sequenceDiagram
participant Temperature Agent
participant hot_or_not Agent
Temperature Agent->>hot_or_not Agent: get_temperature
hot_or_not Agent->>hot_or_not Agent: compare_temperature
```
<!-- MERMAID_END -->

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

If you already created the agents and enabled the tool: `maestro run ./demos/workflows/weather-checker.ai/workflow.yaml`

OR

Directly deploy the workflow via streamlit: `maestro deploy ./demos/workflows/weather-checker.ai/agents.yaml ./demos/workflows/weather-checker.ai/workflow.yaml`
(To run for a different city, change the `prompt` field in `workflow.yaml`, or directly as a prompt in the UI)

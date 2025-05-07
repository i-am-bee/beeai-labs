TODO the demo does not currently function out of the box as the workflow schema / automation are not supported by the demo as of yet.  Merging this early and will address after we've moved name/repos.

# Activity-Planner example

A multi-agent workflow using Maestro to check if the current temperature in a location is hotter or colder than average and recommend activities to do based on the weather.

## Mermaid Diagram

<!-- MERMAID_START -->
```mermaid
sequenceDiagram
participant current_temperature
participant hot_or_not
participant cold_activities
participant hot_activities
current_temperature->>hot_or_not: get-temperature
hot_or_not->>cold_activities: hot-or-not
hot_or_not->>cold_activities: (input.find('hotter') != -1)
alt if True
  hot_or_not->>cold_activities: hot-activities
else is False
  cold_activities->>hot_or_not: cold-activities
end
cold_activities->>hot_activities: cold-activities
hot_activities->>hot_activities: hot-activities
hot_activities->>hot_activities: exit
```
<!-- MERMAID_END -->

## Getting Started

* Run a local instance of the [bee-stack](https://github.com/i-am-bee/bee-stack/blob/main/README.md)

* Verify a valid llm is available to bee-stack

* Install [maestro](https://github.com/i-am-bee/beeai-labs) dependencies: `cd ../../../maestro && poetry shell && poetry install && cd -`

* Configure environmental variables: `cp example.env .env`

* Copy `.env` to common directory: `cp .env ./../common/src`

* Set up the demo and create the agents: `./setup.sh`

* Run the workflow: `./run.sh` (to run for a different city, change the `prompt` field in `workflow.yaml`)

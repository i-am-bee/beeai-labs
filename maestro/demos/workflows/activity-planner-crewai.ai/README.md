# Introduction

This is a simple demonstration of a workflow that uses a third party agent - in this case crew.ai

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

# Requirements

* Python 3.11/3.12
* A valid project environment set-up by running the following from the root of the repository:
  * `poetry shell`
  * `poetry install`

# Running

* Run `demos/activity-planner-crewai.ai/run.py` via shell command line, or IDE such as vscode

# Caveats

* Demo is incomplete and still being worked on including but not limited to
  * Output from current agent cannot be parsed
* `run.sh`, `doctor.sh`. `setup.sh` are currently not implemented
* Demo is likely to be merged with `../activity-planner.ai`
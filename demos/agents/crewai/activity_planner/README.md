# Crew AI Activity Planner

Simple agent which given a prompt including a city, will suggest things to do in the cold or wet weather

Primarily this is to support a demonstration of how a Crew.AI Crew can be integrated into Maestro.  Note that a crew can be composed of multiple agents

# Requirements

* Python 3.11/3.12
* A valid project environment set-up by running the following from the root of the repository:
  * `poetry shell`
  * `poetry install`

# Running

* Run `demos/agents/crewai/activity_planner.py` via shell command line, or IDE such as vscode

## Future enhancements

- The agent could be made more generic to deal with both hot and cold weather
- Multiple sources (search engines) could be used to improve the quality of the output
- The number of activities suggested could be adjusted depending on the prompt
- Scripts can be packaged into the module
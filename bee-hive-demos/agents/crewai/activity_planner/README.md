# Crew AI Activity Planner

Simple agent which given a prompt including a city, will suggest things to do in the cold or wet weather

Primarily this is to demonstrate how a Crew.AI Crew can be integrated into beehive.  Note that a crew can be composed of multiple agents

## Usage

### Setup

- `poetry shell`
- `poetry install`

### Run

- `./run.sh`

### Test

- `./test.sh`

Note that this currently does the same as run

## Future enhancements

- The agent could be made more generic to deal with both hot and cold weather
- Multiple sources (search engines) could be used to improve the quality of the output
- The number of activities suggested could be adjusted depending on the prompt
- Scripts can be packaged into the module
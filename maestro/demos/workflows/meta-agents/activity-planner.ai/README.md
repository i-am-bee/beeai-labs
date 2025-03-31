# Meta Agents V2

This is the second iteration of meta agents, improved from weather-checker meta-agents.

The prompts now are completely generic, and we can recreate the activity-planner and weather comparison demos using natural language and nothing else.

The agents folder has the meta agents/workflow definitions that create the agents.yaml file, and similarly for the workflow.

To run from maestro level:

Creating agents:
`maestro create ./demos/workflows/meta-agents/activity-planner.ai/FOLDER_NAME/AGENTS_FILE_NAME`
Running workflow:
`maestro run None ./demos/workflows/meta-agents/activity-planner.ai/FOLDER_NAME/WORKFLOW_FILE_NAME`

You can switch between the activity-planner demo and weather checker prompts:

Activity-planner: I want 4 agents in order to ultimately decide what activities I should do in a given location. First agent get the current temperature given a location, the second to compare that temperature with historical temperatures, then another agent to provide a list of activities if it's cold or conversely another agent to proivde a list of activities if it is hot.

Weather-checker:  I want to compare the current weather with the historical averages. To do this, I will need 2 agents, one to retrieve the weather and one to compare to the historical average.

To deploy:
`maestro deploy ./demos/workflows/meta-agents/activity-planner.ai/FOLDER_NAME/AGENTS_FILE_NAME ./demos/workflows/meta-agents/activity-planner.ai/FOLDER_NAME/WORKFLOW_FILE_NAME --streamlit`
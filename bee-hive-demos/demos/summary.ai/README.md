# Steps to Replicate Summary.ai:

(1) Set up environmental variables

(2) Start an instance of the bee-stack to run in the background

(3) Create agents.yaml, defining your agents (currently, just have one defined)

NOTE: If you don't want to use hive, follow steps 4a - 7a

(4a) Create the agents: `python create_agents.py agents.yaml`
    - go to the agents.yaml file, copy the code portions to create custom tools to use (in the UI)

(5a) Go to the UI, and make sure the necessary tools are enabled, prompts, and code for tools

(6a) Define workflow.yaml (right now is a sequential execution strat, with the other agents commented out)
    - you could change the prompt here based on what topic you are looking for

(7a) Execute the workflow `python run_workflow.py workflow.yaml`

Using hive script (still requires that you have defined the agents and workflow, but now you don't have to run it separately)
(8b) Run `./hive run workflow.yaml`
    - if agents exist in the agent store, it skips creation otherwise it creates for you: Can also run `./hive create agents.yaml`
    - Note: you must enable tools inside the UI, also create the tools manually for now (copy the code inside the agent defintion to create tool)


## What are the agents in this example?

1st agent: search arxiv agent:
given a topic, search for it in arxiv, get top k results

2nd agent: selector agent:
given output results, select the top n results

3rd agents: summary agent:
passing in the top n results, generate a summary for each


** Note: all agents are fully implemented except for the summary agent. This needs to be tweaked, currently we are passing a portion of entire research paper into the agent to summarize to prevent PDF reading issues, as well as token limits.
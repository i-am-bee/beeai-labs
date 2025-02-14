Here, we are running the new version of the Summary demo, but using the CLI tools. Make sure you have the .env files set in the correct places.

Now, we can use commands like `maestro validate SCHEMA_FILE YAML_FILE` or `maestro run AGENTS_FILE WORKFLOW_FILE [options]`.
Make sure you are in bee-hive->maestro when running the command, and then you can test by using `maestro run  ./demos/workflows/summary.ai/test_yaml/agents.yaml ./demos/workflows/summary.ai/test_yaml/workflow.yaml`.


Note: currently the demo is not expected to produce compleletly accurate answers, as we do not have support to stop and turn on the tools yet so the agents don't have correct tools. However, the end to end workflow is working properly.
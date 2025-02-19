#!/bin/bash
# test.sh: Test the workflow using the CLI in dry-run mode.
echo "🧪 Testing workflow (dry-run mode)..."
maestro run ./demos/workflows/summary.ai/test_yaml/agents.yaml ./demos/workflows/summary.ai/test_yaml/workflow.yaml --dry-run
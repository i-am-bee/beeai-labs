#!/bin/bash

cd "$(dirname "$0")/../../../../" || exit 1
echo "📂 Running from: $(pwd)"
export PYTHONPATH="$(pwd):$(pwd)/src"
echo "🐍 PYTHONPATH set to: $PYTHONPATH"

function check_status() {
    if [ $? -ne 0 ]; then
      echo "$1"
      exit 1
    fi
}

echo "🩺 Running environment check..."
./demos/workflows/summary.ai/test_yaml/doctor.sh || exit 1

echo "📝 Validating agents.yaml..."
PYTHONPATH=$PYTHONPATH maestro validate ./schemas/agent_schema.json ./demos/workflows/summary.ai/test_yaml/agents.yaml
check_status "❌ Failed to validate agents.yaml!"

echo "📝 Validating workflow.yaml..."
PYTHONPATH=$PYTHONPATH maestro validate ./schemas/workflow_schema.json ./demos/workflows/summary.ai/test_yaml/workflow.yaml
check_status "❌ Failed to validate workflow.yaml!"

echo "" | PYTHONPATH=$PYTHONPATH maestro run --dry-run ./demos/workflows/summary.ai/test_yaml/agents.yaml ./demos/workflows/summary.ai/test_yaml/workflow.yaml
check_status "❌ Workflow test failed!"


echo "✅ All tests passed!"
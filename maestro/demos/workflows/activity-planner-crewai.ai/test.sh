#! /bin/bash

cd "$(dirname "$0")/../../../" || exit 1

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
poetry run ./demos/workflows/activity-planner-crewai.ai/doctor.sh || exit 1

echo "📝 Validating agents.yaml..."
poetry run maestro validate ./schemas/agent_schema.json ./demos/workflows/activity-planner-crewai.ai/agents.yaml
check_status "❌ Failed to validate agents.yaml!"

echo "📝 Validating workflow.yaml..."
poetry run maestro validate ./schemas/workflow_schema.json ./demos/workflows/activity-planner-crewai.ai/workflow.yaml
check_status "❌ Failed to validate workflow.yaml!"

echo "🧪 Running workflow in dry-run mode..."
echo "" | poetry run maestro run --dry-run ./demos/workflows/activity-planner-crewai.ai/agents.yaml ./demos/workflows/activity-planner-crewai.ai/workflow.yaml
check_status "❌ Workflow test failed!"

echo "✅ All tests passed!"
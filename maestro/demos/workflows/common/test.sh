#!/bin/bash

if [[ -z "$1" ]]; then
    echo "❌ Error: No demo folder specified!"
    echo "Usage: bash test.sh <demo_folder>"
    exit 1
fi

DEMO_DIR="$1"
echo "📂 Running tests for: $DEMO_DIR"

bash "$(dirname "$0")/doctor.sh" || { echo "❌ Environment check failed"; exit 1; }

AGENTS_YAML=$(find "$DEMO_DIR" -maxdepth 1 -type f -name "agents.yaml")
WORKFLOW_YAML=$(find "$DEMO_DIR" -maxdepth 1 -type f -name "workflow.yaml")

if [[ -z "$AGENTS_YAML" || -z "$WORKFLOW_YAML" ]]; then
    echo "❌ Error: Missing agents.yaml or workflow.yaml in $DEMO_DIR"
    exit 1
fi

SCHEMA_DIR=$(find "$(dirname "$0")/../../.." -type d -name "schemas" -print -quit)

if [[ -z "$SCHEMA_DIR" ]]; then
    echo "❌ Error: Could not find schemas/ directory"
    exit 1
fi

AGENT_SCHEMA_PATH="$SCHEMA_DIR/agent_schema.json"
WORKFLOW_SCHEMA_PATH="$SCHEMA_DIR/workflow_schema.json"

echo "🔍 Detected schema directory: $SCHEMA_DIR"
echo "🔍 Using schema file: $AGENT_SCHEMA_PATH"
echo "🔍 Using schema file: $WORKFLOW_SCHEMA_PATH"

echo "📝 Validating $AGENTS_YAML..."
poetry run maestro validate "$AGENT_SCHEMA_PATH" "$AGENTS_YAML" || { echo "❌ Failed to validate agents.yaml!"; exit 1; }

echo "📝 Validating $WORKFLOW_YAML..."
poetry run maestro validate "$WORKFLOW_SCHEMA_PATH" "$WORKFLOW_YAML" || { echo "❌ Failed to validate workflow.yaml!"; exit 1; }

echo "🧪 Running workflow in dry-run mode..."
echo "" | poetry run maestro run --dry-run "$AGENTS_YAML" "$WORKFLOW_YAML" || { echo "❌ Workflow test failed!"; exit 1; }

echo "✅ Workflow tests passed for $DEMO_DIR!"
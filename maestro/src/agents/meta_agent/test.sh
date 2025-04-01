#!/bin/bash

# ✅ Default to `meta_agent/` if no argument is given
META_AGENT_DIR="${1:-$(cd "$(dirname "$0")" && pwd)}"

echo "📂 Running tests for: $META_AGENT_DIR"

bash "$(dirname "$0")/doctor.sh" || { echo "❌ Environment check failed"; exit 1; }

# Find `agents.yaml` (still required)
AGENTS_YAML=$(find "$META_AGENT_DIR" -maxdepth 1 -type f -name "agents.yaml")

# Find all workflow YAML files dynamically
WORKFLOW_FILES=($(find "$META_AGENT_DIR" -maxdepth 1 -type f -name "workflow*.yaml"))

if [[ -z "$AGENTS_YAML" ]]; then
    echo "❌ Error: Missing agents.yaml in $META_AGENT_DIR"
    exit 1
fi

if [[ ${#WORKFLOW_FILES[@]} -eq 0 ]]; then
    echo "❌ Error: No workflow YAML files found in $META_AGENT_DIR"
    exit 1
fi

# Locate schemas directory
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

# Validate agents.yaml - in loose mode, we only warn if validation fails
echo "📝 Validating $AGENTS_YAML..."
if ! poetry run maestro validate "$AGENT_SCHEMA_PATH" "$AGENTS_YAML"; then
    echo "⚠️ Warning: agents.yaml failed validation, but continuing in loose mode."
fi

# Loop through each workflow file and validate/run tests
for WORKFLOW_YAML in "${WORKFLOW_FILES[@]}"; do
    echo "📝 Validating $WORKFLOW_YAML..."
    if ! poetry run maestro validate "$WORKFLOW_SCHEMA_PATH" "$WORKFLOW_YAML"; then
        echo "⚠️ Warning: $WORKFLOW_YAML failed validation, but continuing in loose mode."
    fi

    echo "🧪 Running workflow in dry-run mode for $WORKFLOW_YAML..."
    if ! echo "" | poetry run maestro run --dry-run "$AGENTS_YAML" "$WORKFLOW_YAML"; then
        echo "⚠️ Warning: Workflow test failed for $WORKFLOW_YAML in loose mode."
    else
        echo "✅ Workflow dry-run succeeded for $WORKFLOW_YAML!"
    fi
done

echo "✅ All meta-agent workflow tests completed (loose mode) for $META_AGENT_DIR!"

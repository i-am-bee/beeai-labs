#!/bin/bash

echo "🚀 Running all meta-agent workflow tests in CI..."
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "📂 Running from: $REPO_ROOT"

META_AGENT_DIR="$REPO_ROOT/maestro/src/agents/meta_agent"

if [[ ! -d "$META_AGENT_DIR" ]]; then
    echo "❌ Error: Meta-agent directory not found at $META_AGENT_DIR"
    exit 1
fi

echo "🔍 Verifying Maestro installation..."
cd "$REPO_ROOT/maestro"

# Test if maestro works with or without poetry
if poetry run maestro --help &>/dev/null; then
    MAESTRO_CMD="poetry run maestro"
elif maestro --help &>/dev/null; then
    MAESTRO_CMD="maestro"
else
    echo "❌ Error: maestro is not running correctly!"
    exit 1
fi

echo "✅ Maestro is running correctly using: $MAESTRO_CMD"

EXPECTED_TESTS=0
TEST_COUNT=0

# Run doctor.sh first
echo "🩺 Running doctor.sh for meta_agent..."
cd "$META_AGENT_DIR"
bash doctor.sh || { echo "❌ doctor.sh failed"; exit 1; }

# Run test.sh only once with the directory, instead of looping over workflow files
echo "🧪 Running test.sh for meta_agent directory..."
bash "$META_AGENT_DIR/test.sh" "$META_AGENT_DIR" || { echo "❌ test.sh failed"; exit 1; }
((TEST_COUNT++))

if [[ "$TEST_COUNT" -gt 0 ]]; then
    echo "✅ All meta-agent workflow tests completed successfully!"
else
    echo "❌ Error: No workflow tests were executed!"
    exit 1
fi

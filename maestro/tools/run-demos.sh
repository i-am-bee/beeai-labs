#!/bin/bash

echo "🚀 Running all demos in CI..."
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "📂 Running from: $REPO_ROOT"

WORKFLOWS_DIR="$REPO_ROOT/maestro/demos/workflows"
COMMON_DIR="$REPO_ROOT/maestro/demos/workflows/common"

if [[ ! -d "$WORKFLOWS_DIR" ]]; then
    echo "❌ Error: Workflows directory not found at $WORKFLOWS_DIR"
    exit 1
fi

if [[ ! -d "$COMMON_DIR" ]]; then
    echo "❌ Error: Common directory not found at $COMMON_DIR"
    exit 1
fi

echo "🔍 Verifying Maestro installation..."
cd "$REPO_ROOT/maestro"

# More robust checking for Maestro
if command -v poetry &>/dev/null; then
    echo "Poetry found, checking for maestro..."
    if poetry run which maestro &>/dev/null; then
        MAESTRO_CMD="poetry run maestro"
        echo "✅ Found maestro via poetry"
    elif poetry run python -m maestro --help &>/dev/null; then
        MAESTRO_CMD="poetry run python -m maestro"
        echo "✅ Found maestro module via poetry"
    else
        echo "🔄 Installing maestro via poetry..."
        poetry install
        if poetry run which maestro &>/dev/null; then
            MAESTRO_CMD="poetry run maestro"
            echo "✅ Successfully installed maestro via poetry"
        else
            echo "❌ Error: Could not install maestro via poetry"
            exit 1
        fi
    fi
elif command -v maestro &>/dev/null; then
    MAESTRO_CMD="maestro"
    echo "✅ Found maestro in PATH"
else
    echo "❌ Error: Neither poetry nor maestro found in PATH"
    echo "Please install maestro or poetry first."
    exit 1
fi

echo "✅ Maestro is running correctly using: $MAESTRO_CMD"

# Create a temporary file to track test counts
TEMP_DIR=$(mktemp -d)
EXPECTED_TESTS_FILE="$TEMP_DIR/expected_tests.txt"
TEST_COUNT_FILE="$TEMP_DIR/test_count.txt"

echo "0" > "$EXPECTED_TESTS_FILE"
echo "0" > "$TEST_COUNT_FILE"

find "$WORKFLOWS_DIR" -mindepth 1 -type d -print0 | while IFS= read -r -d '' demo; do
    if [[ "$demo" == "$COMMON_DIR" ]]; then
        echo "⚠️ Skipping common/ directory..."
        continue
    fi

    DEMO_NAME=$(basename "$demo")
    echo -e "\n========================================"
    echo "====== Running demo: $DEMO_NAME ======"
    echo "========================================\n"

    if [[ -f "$demo/agents.yaml" && -f "$demo/workflow.yaml" ]]; then
        echo "🔍 Running tests for $demo"
        CURRENT_EXPECTED=$(cat "$EXPECTED_TESTS_FILE")
        echo $((CURRENT_EXPECTED + 1)) > "$EXPECTED_TESTS_FILE"
        
        echo "🩺 Running common doctor.sh for $demo..."
        cd "$REPO_ROOT/maestro"
        bash "$COMMON_DIR/doctor.sh" || { echo "❌ doctor.sh failed for $demo"; exit 1; }
        
        echo "🧪 Running common test.sh for $demo..."
        cd "$REPO_ROOT/maestro"
        env MAESTRO_DEMO_OLLAMA_MODEL="ollama/llama3.2:3b" echo "" | bash "$COMMON_DIR/test.sh" "$demo" || { echo "❌ test.sh failed for $demo"; exit 1; }
    
        CURRENT_COUNT=$(cat "$TEST_COUNT_FILE")
        echo $((CURRENT_COUNT + 1)) > "$TEST_COUNT_FILE"
    else
        echo "⚠️ Skipping $demo (no agents.yaml or workflow.yaml found)"
    fi
done

EXPECTED_TESTS=$(cat "$EXPECTED_TESTS_FILE")
TEST_COUNT=$(cat "$TEST_COUNT_FILE")
rm -rf "$TEMP_DIR"

if [[ "$TEST_COUNT" -eq "$EXPECTED_TESTS" && "$EXPECTED_TESTS" -gt 0 ]]; then
    echo "✅ All $EXPECTED_TESTS tests completed successfully!"
else
    echo "❌ Error: Not all expected tests were executed! ($TEST_COUNT/$EXPECTED_TESTS)"
    exit 1
fi
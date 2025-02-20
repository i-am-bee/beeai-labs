#!/bin/bash

echo "🚀 Running all demos in CI..."
REPO_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"

echo "📂 Running from: $REPO_ROOT"

WORKFLOWS_DIR="$REPO_ROOT/maestro/demos/workflows"

if [[ ! -d "$WORKFLOWS_DIR" ]]; then
    echo "❌ Error: Workflows directory not found at $WORKFLOWS_DIR"
    exit 1
fi

EXPECTED_TESTS=0
TEST_COUNT=0

for demo in $(find "$WORKFLOWS_DIR" -mindepth 1 -maxdepth 1 -type d); do
    echo "🔍 Looking for test scripts in $demo"

    test_dir=$(find "$demo" -type f \( -name "doctor.sh" -o -name "test.sh" \) -exec dirname {} \; | sort -u | head -n 1)

    if [[ -z "$test_dir" ]]; then
        test_dir="$demo"
    fi

    echo "📂 Using test directory: $test_dir"

    [[ -f "$test_dir/doctor.sh" ]] && ((EXPECTED_TESTS++))
    [[ -f "$test_dir/test.sh" ]] && ((EXPECTED_TESTS++))

    if [[ -f "$test_dir/doctor.sh" ]]; then
        echo "🩺 Running doctor.sh in $test_dir..."
        cd "$REPO_ROOT/maestro"
        poetry run bash "$test_dir/doctor.sh" || { echo "❌ doctor.sh failed in $test_dir"; exit 1; }
        ((TEST_COUNT++))
    else
        echo "⚠️ Warning: doctor.sh not found in $test_dir"
    fi

    if [[ -f "$test_dir/test.sh" ]]; then
        echo "🧪 Running test.sh in $test_dir..."
        cd "$REPO_ROOT/maestro"
        env MAESTRO_DEMO_OLLAMA_MODEL="ollama/llama3.2:3b" poetry run bash "$test_dir/test.sh" || { echo "❌ test.sh failed in $test_dir"; exit 1; }
        ((TEST_COUNT++))
    else
        echo "⚠️ Warning: test.sh not found in $test_dir"
    fi
done

if [[ "$TEST_COUNT" -eq "$EXPECTED_TESTS" && "$EXPECTED_TESTS" -gt 0 ]]; then
    echo "✅ All $EXPECTED_TESTS tests completed successfully!"
else
    echo "❌ Error: Not all expected tests were executed! ($TEST_COUNT/$EXPECTED_TESTS)"
    exit 1
fi

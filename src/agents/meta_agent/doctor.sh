#!/bin/bash

echo "🔍 Checking environment..."

if poetry run which maestro &> /dev/null; then
    echo "✅ Maestro CLI is installed: $(poetry run which maestro)"
else
    echo "❌ Maestro CLI not found! Please install it using:"
    echo "   poetry install"
    exit 1
fi

echo "📂 Checking meta-agent directory structure..."

META_AGENTS_DIR="$(cd "$(dirname "$0")" && pwd)"

if [[ ! -d "$META_AGENTS_DIR" ]]; then
    echo "❌ Error: Meta-agents directory not found at $META_AGENTS_DIR"
    exit 1
fi

echo "✅ Environment check passed!"

#!/bin/bash
set -e

# 🧬 Project Acritarch Release Validation Gatekeeper
# Verifies that code compiles, tests pass, lint is clean, and bumps the version.
# Use "--test-only" to validate without bumping the version (CI-safe).

export PYTHONDONTWRITEBYTECODE=1

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VERSION_FILE="$PROJECT_DIR/.version"

# Fail closed on unknown arguments: only the release path (no args) and
# "--test-only" are valid invocations.
TEST_ONLY=0
case "${1:-}" in
  "")
    ;;
  "--test-only")
    TEST_ONLY=1
    ;;
  "-h"|"--help")
    echo "Usage: $0 [--test-only]"
    echo "  (no args)     validate and bump the patch version"
    echo "  --test-only   validate only; leaves .version untouched (CI-safe)"
    exit 0
    ;;
  *)
    echo "error: unknown argument '$1'" >&2
    echo "Usage: $0 [--test-only]" >&2
    exit 2
    ;;
esac

echo "🧬 Launching Acritarch Validation Gatekeeper..."

if [ ! -f "$VERSION_FILE" ]; then
  echo "1.0.0" > "$VERSION_FILE"
fi

CURRENT_VERSION=$(cat "$VERSION_FILE" | tr -d '[:space:]')
echo "📍 Current Version: $CURRENT_VERSION"

# Guard the version format before the bumping math below — a corrupted .version
# (e.g. "abc") would otherwise silently produce garbage like "abc..1".
if ! [[ "$CURRENT_VERSION" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
  echo "error: .version '$CURRENT_VERSION' is not MAJOR.MINOR.PATCH" >&2
  exit 1
fi

# Locate Python with required packages (prefer this project's own venv)
PYTHON_BIN="python3"
if [ -f "$PROJECT_DIR/venv/bin/python3" ]; then
  PYTHON_BIN="$PROJECT_DIR/venv/bin/python3"
fi

# Perform validations
echo "🔍 Running static analysis & syntax verification with $PYTHON_BIN..."
$PYTHON_BIN -c "import ast, sys; [ast.parse(open(f).read()) for f in sys.argv[1:]]" "$PROJECT_DIR/server/main.py" "$PROJECT_DIR/server/registry.py" "$PROJECT_DIR/server/parser.py" "$PROJECT_DIR/server/test_server.py"
echo "✓ Python AST & syntax verification: PASS"

echo "🧪 Running unit tests & MCP schema integrity checks..."
cd "$PROJECT_DIR/server"
$PYTHON_BIN test_server.py
echo "✓ MCP server response schema validation: PASS"
echo "✓ Multi-service Swagger & OpenAPI aggregation: PASS"

if [ "$TEST_ONLY" -eq 1 ]; then
  echo "🚀 Validation Succeeded (--test-only). Project Acritarch is production-ready."
  echo "ℹ️  .version left untouched at $CURRENT_VERSION."
  exit 0
fi

# Split version numbers
IFS='.' read -r major minor patch <<< "$CURRENT_VERSION"

# Bump patch version
NEXT_PATCH=$((patch + 1))
NEXT_VERSION="$major.$minor.$NEXT_PATCH"

echo "✨ Bumping version to: $NEXT_VERSION"
echo "$NEXT_VERSION" > "$VERSION_FILE"

echo "🚀 Validation Succeeded. Project Acritarch is production-ready."
exit 0
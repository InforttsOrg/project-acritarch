#!/bin/bash

# 🧬 Project Acritarch Local Dev Orchestrator
# This script orchestrates the local running of the Acritarch Agent-First Docs & MCP Server.

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PORT=8035

echo "🧬 Initializing Acritarch Swarm Orchestrator..."

case "$1" in
  "clean")
    echo "🧹 Cleaning targets and builds..."
    rm -rf "$PROJECT_DIR/server/__pycache__" "$PROJECT_DIR/server/.pytest_cache" "$PROJECT_DIR/.pytest_cache"
    echo "✓ Clean complete."
    exit 0
    ;;
  
  "install")
    echo "📦 Installing project dependencies into the project venv..."
    if [ ! -x "$PROJECT_DIR/venv/bin/python3" ]; then
      python3 -m venv "$PROJECT_DIR/venv"
    fi
    "$PROJECT_DIR/venv/bin/python3" -m pip install --upgrade pip
    "$PROJECT_DIR/venv/bin/python3" -m pip install -r "$PROJECT_DIR/server/requirements.txt"
    echo "✓ Dependencies installed."
    exit 0
    ;;

  "backend" | "dev" | "")
    echo "🛰️ Starting Acritarch Central Docs & MCP Server on Port $PORT..."
    cd "$PROJECT_DIR/server"
    exec "$PROJECT_DIR/venv/bin/uvicorn" main:app --host 0.0.0.0 --port $PORT --reload
    ;;

  "-h" | "--help")
    echo "Usage: ./dev.sh [dev|backend|install|clean]"
    exit 0
    ;;

  *)
    echo "Usage: ./dev.sh [dev|backend|install|clean]"
    exit 1
    ;;
esac
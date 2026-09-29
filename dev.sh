#!/bin/zsh

# 🧬 Project Acritarch Local Dev Orchestrator
# This script orchestrates the local running of the Acritarch Agent-First Docs & MCP Server.

PROJECT_DIR="/Users/admin/rttss-sahil/inforttsOrg/projects/acritarch"
PORT=8035

echo "🧬 Initializing Acritarch Swarm Orchestrator..."

case "$1" in
  "clean")
    echo "🧹 Cleaning targets and builds..."
    rm -rf "$PROJECT_DIR/server/__pycache__" "$PROJECT_DIR/server/.pytest_cache"
    echo "✓ Clean complete."
    exit 0
    ;;
  
  "install")
    echo "📦 Installing system and project dependencies..."
    cd "$PROJECT_DIR/server" && pip install -r requirements.txt
    echo "✓ Dependencies installed."
    exit 0
    ;;

  "backend" | "dev" | "")
    echo "🛰️ Starting Acritarch Central Docs & MCP Server on Port $PORT..."
    cd "$PROJECT_DIR/server"
    exec uvicorn main:app --host 0.0.0.0 --port $PORT --reload
    ;;

  *)
    echo "Usage: ./dev.sh [dev|backend|install|clean]"
    exit 1
    ;;
esac

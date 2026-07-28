# 🧬 Project Acritarch — Agent-First Docs & MCP Gateway

> **Status:** Scaffolding & Requirements Layer Complete
> **Operational Domain:** `docs.infortts.com`
> **Private Container Network Port:** `8035`

---

## 🚀 Overview

Acritarch is the decentralized knowledge indexing engine and Model Context Protocol (MCP) gateway for the Infortts Autonomous Swarm. It translates architectural blueprints, code schemas, and active tasks into developer-friendly websites and LLM-scannable protocols, allowing Meeseeks to navigate the codebase with supreme precision.

---

## 📂 Project Directory Structure

```
projects/acritarch/
├── .version               # Semantic version tracking
├── README.md              # Project onboarding & setup instructions
├── task.md                # Core requirements & specifications
├── dev.sh                 # Local dev orchestration script
├── validate-release.sh    # Release verification script
├── server/                # Python/Go MCP Server
│   ├── main.py            # MCP stdio/SSE server
│   ├── requirements.txt
│   └── parser.py          # Markdown structure indexing compiler
└── client/                # High-fidelity static or Flutter web reader
    ├── index.html
    ├── index.css          # Rocky-Vision styling rules
    └── main.js
```

---

## ⚡ Developer Setup & Orchestration

### 1. Requirements Compilation
* **Python SDK:** Python `3.10+` with standard MCP server frameworks or `uv`.
* **Static Assets:** Serve via Caddy or lightweight NodeJS backend.

### 2. Run Local Stack
To build, compile, and run the documentation website alongside the active MCP server concurrently:
```bash
./dev.sh
```

### 3. Release Verification
To verify Markdown parsing, run JSON-RPC schema tests, and auto-bump the semantic version:
```bash
./validate-release.sh
```

# 🧬 Project Acritarch — Agent-First Docs & MCP Gateway

> **Status:** Operational — Swagger API Hub + MCP Gateway serving
> **Operational Domain:** `docs.infortts.site`
> **Private Container Network Port:** `8035`

---

## 🚀 Overview

Acritarch is the decentralized knowledge indexing engine and Model Context Protocol (MCP) gateway for the Infortts Autonomous Swarm. It translates architectural blueprints, code schemas, and active tasks into developer-friendly websites and LLM-scannable protocols, allowing Meeseeks to navigate the codebase with supreme precision.

---

## 📂 Project Directory Structure

```
projects/acritarch/
├── .version               # Semantic version tracking (single source of truth)
├── .github/workflows/ci.yml
├── LICENSE
├── README.md              # Project onboarding & setup instructions
├── dev.sh                 # Local dev orchestration script
├── validate-release.sh    # Release verification script
└── server/                # Python MCP Gateway
    ├── main.py            # FastAPI app: Swagger hub, service registry API, MCP JSON-RPC endpoint
    ├── registry.py        # Multi-service registry + aggregated OpenAPI 3.0 specifications
    ├── parser.py          # Markdown structure indexing compiler
    ├── requirements.txt
    └── test_server.py     # unittest suite run by the release gate
```

### HTTP Surface
| Method | Path | Purpose |
| ------ | ---- | ------- |
| `GET`  | `/health` | Liveness probe + indexed service count |
| `GET`  | `/docs` | Mobile-first Swagger UI hub (`?service=<service_id>`) |
| `GET`  | `/api/services` | Service registry listing (filter with `?category=`) |
| `GET`  | `/api/services/{service_id}` | Full metadata for one service |
| `GET`  | `/api/specs/{service_id}` | Aggregated OpenAPI 3.0 JSON spec |
| `GET`  | `/api/docs/{service_id}/markdown` | Indexed project markdown (README, MINDMAP, AGENTS, …) |
| `GET`  | `/api/search?q=` | Cross-ecosystem endpoint/description search |
| `POST` | `/mcp` | MCP JSON-RPC 2.0 gateway (`tools/list`, `tools/call`) |

---

## ⚡ Developer Setup & Orchestration

### 1. Requirements Compilation
* **Python SDK:** Python `3.10+`. Install server dependencies with `pip install -r server/requirements.txt`.
* **Swarm root:** markdown indexing resolves the swarm checkout automatically
  (`ACRITARCH_INFORTTS_ROOT` → `/opt/infortts` → `/Users/admin/rttss-sahil/inforttsOrg`). Set
  `ACRITARCH_INFORTTS_ROOT` if your checkout lives elsewhere.
* **Static Assets:** The Swagger UI hub is self-contained and served by the FastAPI app itself.

### 2. Run Local Stack
To run the Central Docs & MCP Gateway on port `8035`:
```bash
./dev.sh            # or ./dev.sh backend
./dev.sh install    # install server dependencies
./dev.sh clean      # remove caches
```

### 3. Release Verification
To verify Markdown parsing, run JSON-RPC schema tests without touching the version:
```bash
./validate-release.sh --test-only
```
Omitting `--test-only` performs the same validation and also bumps the patch
version in `.version` (the release path used by maintainers).

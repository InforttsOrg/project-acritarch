"""
Project Acritarch — Centralized Infortts Docs & MCP Gateway Server
Serves multi-service Swagger/OpenAPI documentation, markdown archives, and MCP endpoints.
"""

import os
import json
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from registry import SERVICES, get_all_services, get_service_spec
from parser import get_project_markdown, scan_all_projects

app = FastAPI(
    title="Project Acritarch — Infortts Central Docs & Schema Gateway",
    version="1.0.0",
    description="Centralized OpenAPI/Swagger documentation hub and MCP gateway for the Infortts Autonomous Swarm."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLIENT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "client")


@app.get("/health")
def health_check():
    return {
        "status": "online",
        "service": "project-acritarch",
        "domain": "docs.infortts.site",
        "port": 8035,
        "indexed_services": len(SERVICES)
    }


@app.get("/api/services")
def list_services(category: Optional[str] = None):
    """Returns all registered microservices across the Infortts swarm."""
    services = get_all_services()
    if category:
        services = [s for s in services if s.get("category", "").lower() == category.lower()]
    return {
        "status": "success",
        "total": len(services),
        "services": services
    }


@app.get("/api/services/{service_id}")
def get_service_details(service_id: str):
    """Returns complete metadata and endpoint registry for a single service."""
    sid = service_id.lower()
    if sid not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service_id}' not found in registry")
    return {
        "status": "success",
        "service": SERVICES[sid]
    }


@app.get("/api/specs/{service_id}")
def get_openapi_spec(service_id: str):
    """Returns OpenAPI 3.0 JSON specification for a service."""
    sid = service_id.lower()
    spec = get_service_spec(sid)
    if not spec:
        raise HTTPException(status_code=404, detail=f"OpenAPI spec for '{service_id}' not found")
    return JSONResponse(content=spec)


@app.get("/api/docs/{service_id}/markdown")
def get_markdown_docs(service_id: str):
    """Returns markdown documentation (README, MINDMAP, task.md) for a project."""
    docs = get_project_markdown(service_id.lower())
    return {
        "status": "success",
        "project": service_id,
        "files": docs
    }


@app.get("/api/search")
def global_search(q: str = Query(..., min_length=2)):
    """Searches across all endpoints, descriptions, and tags in the ecosystem."""
    q_clean = q.lower()
    matches = []

    for sid, svc in SERVICES.items():
        # Check service metadata
        svc_match = False
        if q_clean in svc["name"].lower() or q_clean in svc["description"].lower() or any(q_clean in t for t in svc.get("tags", [])):
            svc_match = True

        # Check endpoints
        paths = svc.get("openapi", {}).get("paths", {})
        for path_key, methods in paths.items():
            for method, details in methods.items():
                summary = details.get("summary", "")
                desc = details.get("description", "")
                if q_clean in path_key.lower() or q_clean in summary.lower() or q_clean in desc.lower() or svc_match:
                    matches.append({
                        "service_id": sid,
                        "service_name": svc["name"],
                        "domain": svc["domain"],
                        "port": svc["default_port"],
                        "path": path_key,
                        "method": method.upper(),
                        "summary": summary,
                        "description": desc
                    })

    return {
        "query": q,
        "total_matches": len(matches),
        "results": matches
    }


# MCP JSON-RPC Gateway endpoint
@app.post("/mcp")
def mcp_gateway(payload: Dict[str, Any]):
    """Model Context Protocol (MCP) JSON-RPC handler for autonomous agents."""
    method = payload.get("method")
    params = payload.get("params", {})
    req_id = payload.get("id", 1)

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "tools": [
                    {
                        "name": "list_infortts_services",
                        "description": "Lists all active Infortts microservices, their ports, domains, and responsibilities.",
                        "inputSchema": {"type": "object", "properties": {}}
                    },
                    {
                        "name": "get_service_api_spec",
                        "description": "Retrieves the full OpenAPI 3.0 JSON specification for a specific Infortts service.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "service_id": {"type": "string", "description": "e.g. glycocalyx, mitochondria, spark, prism"}
                            },
                            "required": ["service_id"]
                        }
                    },
                    {
                        "name": "search_ecosystem_apis",
                        "description": "Searches across all endpoints and routes in the entire Infortts ecosystem.",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string", "description": "Search keyword like 'auth', 'stream', 'options', 'events'"}
                            },
                            "required": ["query"]
                        }
                    }
                ]
            }
        }
    elif method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        if tool_name == "list_infortts_services":
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(get_all_services(), indent=2)}]}
            }
        elif tool_name == "get_service_api_spec":
            spec = get_service_spec(args.get("service_id", ""))
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(spec, indent=2)}]}
            }
        elif tool_name == "search_ecosystem_apis":
            q = args.get("query", "")
            res = global_search(q)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }
        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32600, "message": "Invalid Request"}
    }


# Serve Swagger UI Documentation Viewer for any service or aggregated
@app.get("/docs", response_class=HTMLResponse)
def serve_docs_portal(service: Optional[str] = "glycocalyx"):
    target_service = service.lower() if service else "glycocalyx"
    if target_service not in SERVICES:
        target_service = "glycocalyx"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Infortts Swarm API Hub — Project Acritarch</title>
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui.css" />
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
  <style>
    :root {{
      --bg: #070b10;
      --sidebar: #0b1119;
      --surface: #101924;
      --border: #1a2738;
      --steel: #8a9fb5;
      --titanium: #f1f5f9;
      --cyan: #21e6d0;
      --cyan-glow: rgba(33, 230, 208, 0.15);
      --blue: #3b82f6;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      background: var(--bg);
      color: var(--steel);
      font-family: 'Plus Jakarta Sans', -apple-system, sans-serif;
      display: flex;
      height: 100vh;
      overflow: hidden;
    }}
    /* Sidebar */
    .sidebar {{
      width: 290px;
      background: var(--sidebar);
      border-right: 1px solid var(--border);
      display: flex;
      flex-direction: column;
      flex-shrink: 0;
    }}
    .brand {{
      padding: 20px 18px;
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .brand-icon {{
      width: 38px;
      height: 38px;
      border-radius: 10px;
      background: linear-gradient(135deg, #12202e, #0a111a);
      border: 1px solid rgba(33, 230, 208, 0.3);
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 20px;
      box-shadow: 0 0 16px var(--cyan-glow);
    }}
    .brand-title {{
      font-size: 15px;
      font-weight: 700;
      color: var(--titanium);
      letter-spacing: -0.01em;
    }}
    .brand-sub {{
      font-size: 11px;
      color: var(--cyan);
      font-family: 'JetBrains Mono', monospace;
    }}
    .search-box {{
      padding: 14px 16px;
      border-bottom: 1px solid var(--border);
    }}
    .search-input {{
      width: 100%;
      background: #06090e;
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 8px 12px;
      color: var(--titanium);
      font-size: 12px;
      outline: none;
      font-family: inherit;
    }}
    .search-input:focus {{
      border-color: var(--cyan);
    }}
    .service-list {{
      flex: 1;
      overflow-y: auto;
      padding: 12px 8px;
    }}
    .category-label {{
      font-size: 10px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: #52677d;
      font-weight: 700;
      padding: 10px 12px 4px;
    }}
    .service-item {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 9px 12px;
      border-radius: 8px;
      color: var(--steel);
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      margin-bottom: 2px;
      transition: all 0.15s ease;
    }}
    .service-item:hover {{
      background: #101a26;
      color: var(--titanium);
    }}
    .service-item.active {{
      background: rgba(33, 230, 208, 0.1);
      border: 1px solid rgba(33, 230, 208, 0.3);
      color: var(--cyan);
      font-weight: 600;
    }}
    .port-tag {{
      font-family: 'JetBrains Mono', monospace;
      font-size: 10px;
      color: #5f7894;
      background: #080d14;
      padding: 2px 6px;
      border-radius: 4px;
      border: 1px solid #162230;
    }}
    .service-item.active .port-tag {{
      color: var(--cyan);
      border-color: rgba(33, 230, 208, 0.3);
    }}
    
    /* Main Content */
    .main-content {{
      flex: 1;
      display: flex;
      flex-direction: column;
      overflow: hidden;
      background: var(--bg);
    }}
    .top-bar {{
      height: 58px;
      background: var(--sidebar);
      border-bottom: 1px solid var(--border);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 24px;
    }}
    .service-header {{
      display: flex;
      align-items: center;
      gap: 12px;
    }}
    .current-svc-name {{
      color: var(--titanium);
      font-size: 16px;
      font-weight: 700;
    }}
    .current-svc-domain {{
      color: var(--cyan);
      font-family: 'JetBrains Mono', monospace;
      font-size: 12px;
      background: rgba(33, 230, 208, 0.08);
      border: 1px solid rgba(33, 230, 208, 0.2);
      padding: 3px 10px;
      border-radius: 12px;
    }}
    .docs-scroll {{
      flex: 1;
      overflow-y: auto;
      padding: 24px 32px;
    }}

    /* Custom Swagger UI Overrides for Obsidian Dark Theme */
    .swagger-ui {{
      font-family: inherit !important;
      color: var(--steel) !important;
    }}
    .swagger-ui .info {{
      margin: 20px 0 !important;
    }}
    .swagger-ui .info .title {{
      color: var(--titanium) !important;
      font-size: 24px !important;
      font-weight: 700 !important;
    }}
    .swagger-ui .info p, .swagger-ui .info li {{
      color: var(--steel) !important;
      font-size: 14px !important;
    }}
    .swagger-ui .scheme-container {{
      background: var(--surface) !important;
      box-shadow: none !important;
      border: 1px solid var(--border) !important;
      border-radius: 12px !important;
      padding: 16px !important;
      margin-bottom: 24px !important;
    }}
    .swagger-ui .opblock {{
      background: #0a0f16 !important;
      border: 1px solid var(--border) !important;
      border-radius: 10px !important;
      margin-bottom: 12px !important;
      box-shadow: none !important;
    }}
    .swagger-ui .opblock .opblock-summary {{
      padding: 10px 14px !important;
    }}
    .swagger-ui .opblock .opblock-summary-path {{
      color: var(--titanium) !important;
      font-family: 'JetBrains Mono', monospace !important;
      font-size: 13px !important;
    }}
    .swagger-ui .opblock .opblock-summary-description {{
      color: var(--steel) !important;
      font-size: 12px !important;
    }}
    .swagger-ui .opblock-body {{
      background: #070b11 !important;
    }}
    .swagger-ui .tabli button {{
      color: var(--steel) !important;
    }}
    .swagger-ui table thead tr th, .swagger-ui table tbody tr td {{
      color: var(--steel) !important;
      border-bottom: 1px solid var(--border) !important;
    }}
    .swagger-ui .btn {{
      border-radius: 8px !important;
      border-color: var(--border) !important;
      color: var(--titanium) !important;
    }}
    .swagger-ui .btn.execute {{
      background-color: var(--cyan) !important;
      color: #050b12 !important;
      font-weight: 700 !important;
      border: 0 !important;
    }}
    .swagger-ui select {{
      background: #0d1520 !important;
      color: var(--titanium) !important;
      border-color: var(--border) !important;
    }}
    .swagger-ui input[type=text], .swagger-ui textarea {{
      background: #080d14 !important;
      color: var(--titanium) !important;
      border: 1px solid var(--border) !important;
      border-radius: 6px !important;
    }}
    .swagger-ui .response-col_status {{
      color: var(--titanium) !important;
    }}
  </style>
</head>
<body>

  <aside class="sidebar">
    <div class="brand">
      <div class="brand-icon">🧬</div>
      <div>
        <div class="brand-title">Project Acritarch</div>
        <div class="brand-sub">Infortts Swarm Docs Hub</div>
      </div>
    </div>

    <div class="search-box">
      <input type="text" class="search-input" id="searchFilter" placeholder="Filter microservices or routes..." />
    </div>

    <div class="service-list" id="servicesNav">
      <div class="category-label">Ecosystem Gateways</div>
      <a href="/docs?service=glycocalyx" class="service-item {"active" if target_service == "glycocalyx" else ""}">
        <span>🧬 Glycocalyx Auth</span>
        <span class="port-tag">:8020</span>
      </a>
      <a href="/docs?service=spark" class="service-item {"active" if target_service == "spark" else ""}">
        <span>⚡ Spark Gateway</span>
        <span class="port-tag">:8080</span>
      </a>

      <div class="category-label">Quant & Telemetry</div>
      <a href="/docs?service=mitochondria" class="service-item {"active" if target_service == "mitochondria" else ""}">
        <span>⚡ Mitochondria HFT</span>
        <span class="port-tag">:9910</span>
      </a>
      <a href="/docs?service=cardiodictyon" class="service-item {"active" if target_service == "cardiodictyon" else ""}">
        <span>🫀 Cardiodictyon Vital</span>
        <span class="port-tag">:9911</span>
      </a>
      <a href="/docs?service=wiwaxia" class="service-item {"active" if target_service == "wiwaxia" else ""}">
        <span>🔬 Wiwaxia Compute</span>
        <span class="port-tag">:9902</span>
      </a>

      <div class="category-label">Intelligence & Agents</div>
      <a href="/docs?service=primata" class="service-item {"active" if target_service == "primata" else ""}">
        <span>🧠 Primata Core</span>
        <span class="port-tag">:8006</span>
      </a>
      <a href="/docs?service=prism" class="service-item {"active" if target_service == "prism" else ""}">
        <span>📊 Prism Analytics</span>
        <span class="port-tag">:8005</span>
      </a>
      <a href="/docs?service=cyanobacteria" class="service-item {"active" if target_service == "cyanobacteria" else ""}">
        <span>🦠 Cyanobacteria Brain</span>
        <span class="port-tag">:8010</span>
      </a>

      <div class="category-label">Security & Network Mesh</div>
      <a href="/docs?service=orthrozanclus" class="service-item {"active" if target_service == "orthrozanclus" else ""}">
        <span>🛡️ Orthrozanclus SIEM</span>
        <span class="port-tag">:9912</span>
      </a>
      <a href="/docs?service=ernietta" class="service-item {"active" if target_service == "ernietta" else ""}">
        <span>🌐 Ernietta Fabric</span>
        <span class="port-tag">:9913</span>
      </a>
      <a href="/docs?service=pikaia" class="service-item {"active" if target_service == "pikaia" else ""}">
        <span>🌿 Pikaia RBAC</span>
        <span class="port-tag">:8040</span>
      </a>
    </div>
  </aside>

  <main class="main-content">
    <header class="top-bar">
      <div class="service-header">
        <span class="current-svc-name">{SERVICES.get(target_service, {}).get("name", "Infortts API")}</span>
        <span class="current-svc-domain">{SERVICES.get(target_service, {}).get("domain", "infortts.site")}</span>
      </div>
      <div>
        <a href="/api/specs/{target_service}" target="_blank" style="color:var(--cyan);font-size:12px;text-decoration:none;font-family:'JetBrains Mono',monospace;">Raw OpenAPI Spec →</a>
      </div>
    </header>

    <div class="docs-scroll">
      <div id="swagger-ui"></div>
    </div>
  </main>

  <script src="https://unpkg.com/swagger-ui-dist@5.11.0/swagger-ui-bundle.js"></script>
  <script>
    const specUrl = '/api/specs/{target_service}';
    window.ui = SwaggerUIBundle({{
      url: specUrl,
      dom_id: '#swagger-ui',
      deepLinking: true,
      presets: [
        SwaggerUIBundle.presets.apis,
        SwaggerUIBundle.SwaggerUIStandalonePreset
      ],
      layout: "BaseLayout"
    }});

    // Live filter search
    document.getElementById('searchFilter').addEventListener('input', function(e) {{
      const q = e.target.value.toLowerCase();
      document.querySelectorAll('.service-item').forEach(item => {{
        const text = item.textContent.toLowerCase();
        item.style.display = text.includes(q) ? 'flex' : 'none';
      }});
    }});
  </script>
</body>
</html>
"""

# Default route redirects to /docs
@app.get("/", response_class=HTMLResponse)
def root_index():
    return serve_docs_portal("glycocalyx")

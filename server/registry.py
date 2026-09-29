"""
Infortts Ecosystem Service Registry & Schema Definitions
Central source of truth for all microservice APIs, routes, ports, and metadata.
"""

from typing import Dict, Any, List

SERVICES: Dict[str, Dict[str, Any]] = {
    "glycocalyx": {
        "id": "glycocalyx",
        "name": "Glycocalyx Auth Gateway",
        "category": "Identity & Security",
        "domain": "auth.infortts.site",
        "default_port": 8020,
        "runtime": "Go / Chi / WebAuthn",
        "repo": "InforttsOrg/glycocalyx",
        "description": "Enterprise multi-tenant authentication gateway, FIDO2/Passkey biometrics, Google OAuth SSO, session management, and JWT issuer.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/docs/openapi.json",
        "tags": ["auth", "security", "passkeys", "oauth", "sso", "profile"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {
                "title": "Glycocalyx Auth Gateway API",
                "version": "2.1.0",
                "description": "Authentication and user security microservice for the Infortts Swarm."
            },
            "servers": [
                {"url": "https://auth.infortts.site", "description": "Production VPS Gateway"},
                {"url": "http://localhost:8020", "description": "Local Dev Instance"}
            ],
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health Check",
                        "description": "Returns operational and database connectivity status.",
                        "responses": {
                            "200": {"description": "Service healthy"}
                        }
                    }
                },
                "/auth/login": {
                    "post": {
                        "summary": "User Login",
                        "description": "Authenticate using email and credentials.",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["email", "password"],
                                        "properties": {
                                            "email": {"type": "string", "format": "email"},
                                            "password": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "JWT session token and cookie issued"},
                            "401": {"description": "Invalid credentials"}
                        }
                    }
                },
                "/auth/register": {
                    "post": {
                        "summary": "User Registration",
                        "description": "Register a new enterprise account with password and profile verification.",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["name", "email", "password"],
                                        "properties": {
                                            "name": {"type": "string"},
                                            "email": {"type": "string", "format": "email"},
                                            "password": {"type": "string", "minLength": 8}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "201": {"description": "Account created successfully"},
                            "400": {"description": "Validation error or email exists"}
                        }
                    }
                },
                "/auth/google": {
                    "post": {
                        "summary": "Google OAuth SSO",
                        "description": "Exchange Google ID token for Glycocalyx session JWT.",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["id_token"],
                                        "properties": {
                                            "id_token": {"type": "string"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Authenticated successfully"}
                        }
                    }
                },
                "/auth/passkeys/assertion/options": {
                    "post": {
                        "summary": "Passkey Assertion Options",
                        "description": "Generates WebAuthn cryptographic challenge for biometric authentication.",
                        "responses": {
                            "200": {"description": "WebAuthn challenge payload"}
                        }
                    }
                },
                "/auth/passkeys/assertion/verify": {
                    "post": {
                        "summary": "Passkey Assertion Verification",
                        "description": "Verifies signature against registered public keys.",
                        "responses": {
                            "200": {"description": "Passkey verified; session created"}
                        }
                    }
                },
                "/user/profile": {
                    "get": {
                        "summary": "Get User Profile",
                        "security": [{"BearerAuth": []}],
                        "responses": {
                            "200": {"description": "User profile, roles, and connected devices"}
                        }
                    }
                },
                "/user/devices": {
                    "get": {
                        "summary": "List Connected Devices & Active Sessions",
                        "security": [{"BearerAuth": []}],
                        "responses": {
                            "200": {"description": "Array of active sessions and IP geolocations"}
                        }
                    }
                }
            },
            "components": {
                "securitySchemes": {
                    "BearerAuth": {
                        "type": "http",
                        "scheme": "bearer",
                        "bearerFormat": "JWT"
                    }
                }
            }
        }
    },
    "mitochondria": {
        "id": "mitochondria",
        "name": "Mitochondria Forensics & Trading Engine",
        "category": "Quant & Telemetry",
        "domain": "forensics.infortts.site",
        "default_port": 9910,
        "runtime": "C++ 20 / WASM / Python",
        "repo": "InforttsOrg/mitochondria",
        "description": "Nanosecond-latency institutional options pricing, Black-Scholes/Binomial engine, multi-leg strategy analysis, and MT5 live broker stream.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/docs/openapi.json",
        "tags": ["quant", "trading", "options", "black-scholes", "forensics", "stream"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {
                "title": "Mitochondria C++ Edge Options & Forensics API",
                "version": "1.4.0",
                "description": "High-performance derivatives computation and trade execution stream."
            },
            "servers": [
                {"url": "https://forensics.infortts.site", "description": "Production Forensics Node"},
                {"url": "http://localhost:9910", "description": "Local C++ Server"}
            ],
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health Check",
                        "responses": {"200": {"description": "C++ Edge Backend online"}}
                    }
                },
                "/api/v1/options/price": {
                    "post": {
                        "summary": "Calculate Option Price & Greeks",
                        "description": "Compute Black-Scholes or Binomial American/European option valuation and first/second order Greeks.",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["type", "underlying", "strike", "expiry"],
                                        "properties": {
                                            "type": {"type": "string", "enum": ["call", "put"]},
                                            "style": {"type": "string", "enum": ["european", "american"], "default": "european"},
                                            "underlying": {"type": "number", "example": 100.0},
                                            "strike": {"type": "number", "example": 105.0},
                                            "expiry": {"type": "number", "description": "Years to expiry", "example": 0.25},
                                            "rate": {"type": "number", "example": 0.05},
                                            "iv": {"type": "number", "description": "Implied volatility (0.3 = 30%)", "example": 0.3},
                                            "dividend_yield": {"type": "number", "default": 0.0}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Price, intrinsic value, time value, and Delta/Gamma/Theta/Vega/Rho"}
                        }
                    }
                },
                "/api/v1/options/iv": {
                    "post": {
                        "summary": "Compute Implied Volatility",
                        "description": "Numerically solves Black-Scholes inversion for exact implied volatility.",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "required": ["type", "underlying", "strike", "expiry", "market_price"],
                                        "properties": {
                                            "type": {"type": "string", "enum": ["call", "put"]},
                                            "underlying": {"type": "number"},
                                            "strike": {"type": "number"},
                                            "expiry": {"type": "number"},
                                            "market_price": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {"description": "Implied volatility result"}
                        }
                    }
                },
                "/api/v1/options/strategies/vertical-spread": {
                    "post": {
                        "summary": "Analyze Vertical Spread Strategy",
                        "description": "Simulate bull/bear debit or credit vertical spread with max profit, max loss, break-even, and probability of profit.",
                        "responses": {"200": {"description": "Strategy metrics and risk profile"}}
                    }
                },
                "/api/v1/options/strategies/iron-condor": {
                    "post": {
                        "summary": "Analyze Iron Condor Strategy",
                        "description": "Calculates 4-leg Iron Condor spread probability distribution.",
                        "responses": {"200": {"description": "Iron condor risk and yield analysis"}}
                    }
                },
                "/api/mitochondria/backtest": {
                    "post": {
                        "summary": "Run Micro-Backtest",
                        "responses": {"200": {"description": "Sharpe ratio, profit factor, win rate"}}
                    }
                }
            }
        }
    },
    "spark": {
        "id": "spark",
        "name": "Spark API Gateway & Match Engine",
        "category": "Networking & Gateway",
        "domain": "spark.infortts.site",
        "default_port": 8080,
        "runtime": "Go / Gin / Redis",
        "repo": "InforttsOrg/spark",
        "description": "High-throughput real-time geo-spatial matching, WebSocket connection orchestrator, and discovery engine.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/docs/openapi.json",
        "tags": ["gateway", "routing", "discovery", "matching", "websocket"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {
                "title": "Spark API Gateway & Core Matcher",
                "version": "1.0.0",
                "description": "Core routing, location matching, and profile synchronization gateway."
            },
            "servers": [
                {"url": "https://spark.infortts.site", "description": "Production VPS Gateway"},
                {"url": "http://localhost:8080", "description": "Local Gateway"}
            ],
            "paths": {
                "/health": {
                    "get": {
                        "summary": "System Health",
                        "responses": {"200": {"description": "Gateway online"}}
                    }
                },
                "/api/v1/discovery/feed": {
                    "get": {
                        "summary": "Get Ranked Discovery Feed",
                        "description": "Fetches geo-targeted and vector-matched profile feed.",
                        "responses": {"200": {"description": "Array of candidate entities"}}
                    }
                },
                "/api/v1/location/update": {
                    "post": {
                        "summary": "Update Geo Coordinates",
                        "responses": {"200": {"description": "Location indexed in Redis geo spatial index"}}
                    }
                },
                "/api/v1/matches": {
                    "get": {
                        "summary": "Active Matches",
                        "responses": {"200": {"description": "List of active matched entities"}}
                    }
                }
            }
        }
    },
    "prism": {
        "id": "prism",
        "name": "Prism Multi-Tenant Analytics",
        "category": "Intelligence & Analytics",
        "domain": "prism.infortts.site",
        "default_port": 8005,
        "runtime": "Python / FastAPI",
        "repo": "InforttsOrg/prism",
        "description": "Vector analytics, multi-tenant telemetry aggregation, event logging, and real-time dashboard data pipelines.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/openapi.json",
        "tags": ["analytics", "metrics", "telemetry", "events", "dashboards"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {
                "title": "Prism Analytics & Event Ingestion API",
                "version": "1.2.0",
                "description": "High-throughput analytical event pipeline and visualization query layer."
            },
            "servers": [
                {"url": "https://prism.infortts.site", "description": "Production Analytics Node"},
                {"url": "http://localhost:8005", "description": "Local Server"}
            ],
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health Check",
                        "responses": {"200": {"description": "Analytics engine online"}}
                    }
                },
                "/api/events/track": {
                    "post": {
                        "summary": "Track Telemetry Event",
                        "description": "Ingest structured system event, performance metric, or user interaction.",
                        "responses": {"202": {"description": "Event queued for ingestion"}}
                    }
                },
                "/api/metrics/aggregate": {
                    "get": {
                        "summary": "Get Aggregated Time-Series",
                        "responses": {"200": {"description": "Time-series aggregations with p95, p99 latencies"}}
                    }
                }
            }
        }
    },
    "primata": {
        "id": "primata",
        "name": "Primata Multi-Agent Intelligence Core",
        "category": "Autonomous Agents",
        "domain": "primata.infortts.site",
        "default_port": 8006,
        "runtime": "Python / FastAPI",
        "repo": "InforttsOrg/primata",
        "description": "Autonomous task synthesis, prompt routing, tool calling executor, and multi-model consensus generator.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/openapi.json",
        "tags": ["agents", "ai", "llm", "synthesis", "consensus"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {
                "title": "Primata Intelligence Core API",
                "version": "1.0.0",
                "description": "Autonomous multi-agent orchestration and task execution service."
            },
            "servers": [
                {"url": "https://primata.infortts.site", "description": "Production Agent Node"},
                {"url": "http://localhost:8006", "description": "Local Server"}
            ],
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health Check",
                        "responses": {"200": {"description": "Primata ready"}}
                    }
                },
                "/api/tasks/synthesize": {
                    "post": {
                        "summary": "Synthesize Autonomous Task Plan",
                        "responses": {"200": {"description": "Structured DAG of subagent tasks"}}
                    }
                }
            }
        }
    },
    "cyanobacteria": {
        "id": "cyanobacteria",
        "name": "Cyanobacteria Autonomous Swarm Brain",
        "category": "Autonomous Agents",
        "domain": "cyanobacteria.infortts.site",
        "default_port": 8010,
        "runtime": "Go Gateway / Python FastAPI Brain",
        "repo": "InforttsOrg/cyanobacteria",
        "description": "Background task worker mesh, continuous learning agent loops, and memory graph synchronizer.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/docs/openapi.json",
        "tags": ["swarm", "brain", "learning", "workers"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {
                "title": "Cyanobacteria Swarm Brain API",
                "version": "1.1.0",
                "description": "Swarm control and agent life-cycle manager."
            },
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health Check",
                        "responses": {"200": {"description": "Brain online"}}
                    }
                },
                "/api/swarm/status": {
                    "get": {
                        "summary": "Get Swarm Node Topology",
                        "responses": {"200": {"description": "Active agent workers and allocations"}}
                    }
                }
            }
        }
    },
    "cardiodictyon": {
        "id": "cardiodictyon",
        "name": "Cardiodictyon Biomedical Telemetry",
        "category": "Biomedical & IoT",
        "domain": "telemetry.infortts.site",
        "default_port": 9911,
        "runtime": "C++ / React",
        "repo": "InforttsOrg/cardiodictyon",
        "description": "Cardiovascular sensory telemetry stream, ECG wavelet signal analysis, and real-time biometric vital monitoring.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/docs/openapi.json",
        "tags": ["telemetry", "biomedical", "sensors", "wavelet", "ecg"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {
                "title": "Cardiodictyon Telemetry API",
                "version": "1.0.0",
                "description": "Real-time biometric data stream and signal processing."
            },
            "paths": {
                "/health": {
                    "get": {
                        "summary": "Health Check",
                        "responses": {"200": {"description": "Telemetry stream online"}}
                    }
                },
                "/api/v1/telemetry/stream": {
                    "get": {
                        "summary": "Biometric Sensory Data Feed",
                        "responses": {"200": {"description": "Stream packet payload"}}
                    }
                }
            }
        }
    },
    "wiwaxia": {
        "id": "wiwaxia",
        "name": "Wiwaxia Algorithmic Computation Bridge",
        "category": "Core Utilities",
        "domain": "wiwaxia.infortts.site",
        "default_port": 9902,
        "runtime": "C++ / Python",
        "repo": "InforttsOrg/wiwaxia",
        "description": "Cryptographic scale hashing, array manipulation, and fast matrix operations.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/docs/openapi.json",
        "tags": ["compute", "crypto", "matrix"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {"title": "Wiwaxia Computation API", "version": "1.0.0"},
            "paths": {
                "/health": {"get": {"summary": "Health Check", "responses": {"200": {"description": "Online"}}}}
            }
        }
    },
    "orthrozanclus": {
        "id": "orthrozanclus",
        "name": "Orthrozanclus Deep Neural Anomaly Router",
        "category": "Security & Defense",
        "domain": "orthrozanclus.infortts.site",
        "default_port": 9912,
        "runtime": "C++",
        "repo": "InforttsOrg/orthrozanclus",
        "description": "Zero-trust network intrusion detection and packet-level deep anomaly classifier.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/docs/openapi.json",
        "tags": ["security", "siem", "firewall", "anomaly"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {"title": "Orthrozanclus Anomaly Router API", "version": "1.0.0"},
            "paths": {
                "/health": {"get": {"summary": "Health Check", "responses": {"200": {"description": "Active"}}}}
            }
        }
    },
    "ernietta": {
        "id": "ernietta",
        "name": "Ernietta High-Throughput Network Fabric",
        "category": "Networking & Gateway",
        "domain": "ernietta.infortts.site",
        "default_port": 9913,
        "runtime": "C++ / eBPF",
        "repo": "InforttsOrg/ernietta",
        "description": "Decentralized mesh routing, eBPF packet filter, and inter-node tunnel manager.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/docs/openapi.json",
        "tags": ["network", "ebpf", "mesh", "tunnel"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {"title": "Ernietta Network Fabric API", "version": "1.0.0"},
            "paths": {
                "/health": {"get": {"summary": "Health Check", "responses": {"200": {"description": "Active"}}}}
            }
        }
    },
    "pikaia": {
        "id": "pikaia",
        "name": "Pikaia Ecosystem Health & RBAC",
        "category": "Governance & RBAC",
        "domain": "pikaia.infortts.site",
        "default_port": 8040,
        "runtime": "Go / Python",
        "repo": "InforttsOrg/pikaia",
        "description": "Ecosystem node health, RBAC provisioning, node registry, and infrastructure guardrails.",
        "health_path": "/health",
        "docs_path": "/docs",
        "spec_path": "/docs/openapi.json",
        "tags": ["health", "rbac", "governance", "admin"],
        "openapi": {
            "openapi": "3.0.3",
            "info": {"title": "Pikaia Governance & Health API", "version": "1.0.0"},
            "paths": {
                "/health": {"get": {"summary": "Health Check", "responses": {"200": {"description": "Active"}}}}
            }
        }
    }
}


def get_all_services() -> List[Dict[str, Any]]:
    return [
        {
            "id": s["id"],
            "name": s["name"],
            "category": s["category"],
            "domain": s["domain"],
            "default_port": s["default_port"],
            "runtime": s["runtime"],
            "repo": s["repo"],
            "description": s["description"],
            "health_path": s["health_path"],
            "docs_path": s["docs_path"],
            "tags": s["tags"],
            "endpoints_count": len(s.get("openapi", {}).get("paths", {}))
        }
        for s in SERVICES.values()
    ]


def get_service_spec(service_id: str) -> Dict[str, Any]:
    svc = SERVICES.get(service_id.lower())
    if not svc:
        return {}
    return svc.get("openapi", {})

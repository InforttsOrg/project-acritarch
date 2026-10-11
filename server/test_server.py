"""
Standalone Unit Tests for Project Acritarch Docs & MCP Server
Validates OpenAPI specifications, service registry, MCP tools, and markdown indexing.
"""

import unittest
import json
import os
import sys

# Ensure server package is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from registry import SERVICES, get_all_services, get_service_spec
from parser import get_project_markdown, scan_all_projects


class TestAcritarchCore(unittest.TestCase):

    def test_services_registry(self):
        """Validates that all core services are properly indexed with required metadata."""
        services = get_all_services()
        self.assertGreater(len(services), 5)
        
        required_keys = ["id", "name", "category", "domain", "default_port", "runtime", "repo", "description", "health_path", "docs_path", "tags", "endpoints_count"]
        for svc in services:
            for k in required_keys:
                self.assertIn(k, svc, f"Service {svc.get('id')} missing key {k}")
            self.assertGreater(svc["endpoints_count"], 0, f"Service {svc['id']} has no documented endpoints")

    def test_openapi_specs_integrity(self):
        """Validates OpenAPI 3.0 structural compliance for all services."""
        core_services = ["glycocalyx", "mitochondria", "spark", "prism", "primata", "cyanobacteria", "cardiodictyon"]
        for sid in core_services:
            spec = get_service_spec(sid)
            self.assertTrue(spec, f"OpenAPI spec for {sid} is empty")
            self.assertTrue(spec.get("openapi", "").startswith("3."), f"Spec for {sid} is not OpenAPI 3.x")
            self.assertIn("info", spec)
            self.assertIn("title", spec["info"])
            self.assertIn("paths", spec)
            self.assertGreater(len(spec["paths"]), 0)

    def test_search_resolution(self):
        """Tests keyword search across microservice paths and descriptions."""
        from main import global_search
        res = global_search("options")
        self.assertGreater(res["total_matches"], 0)
        matched_svcs = [r["service_id"] for r in res["results"]]
        self.assertIn("mitochondria", matched_svcs)

        auth_res = global_search("auth")
        self.assertGreater(auth_res["total_matches"], 0)
        auth_svcs = [r["service_id"] for r in auth_res["results"]]
        self.assertIn("glycocalyx", auth_svcs)

    def test_mcp_gateway_payloads(self):
        """Tests MCP JSON-RPC 2.0 protocol request and response generation."""
        from main import mcp_gateway

        # Test tools/list
        list_req = {"method": "tools/list", "params": {}, "id": 1}
        list_resp = mcp_gateway(list_req)
        self.assertEqual(list_resp.get("jsonrpc"), "2.0")
        tools = [t["name"] for t in list_resp["result"]["tools"]]
        self.assertIn("list_infortts_services", tools)
        self.assertIn("get_service_api_spec", tools)
        self.assertIn("search_ecosystem_apis", tools)

        # Test tools/call: list_infortts_services
        call_req = {
            "method": "tools/call",
            "params": {"name": "list_infortts_services", "arguments": {}},
            "id": 2
        }
        call_resp = mcp_gateway(call_req)
        self.assertEqual(call_resp.get("jsonrpc"), "2.0")
        text = call_resp["result"]["content"][0]["text"]
        self.assertIn("glycocalyx", text)
        self.assertIn("auth.infortts.site", text)

        # Test tools/call: get_service_api_spec
        spec_req = {
            "method": "tools/call",
            "params": {"name": "get_service_api_spec", "arguments": {"service_id": "glycocalyx"}},
            "id": 3
        }
        spec_resp = mcp_gateway(spec_req)
        spec_text = spec_resp["result"]["content"][0]["text"]
        self.assertIn("/auth/login", spec_text)

    def test_markdown_parser(self):
        """Tests the markdown scanner against a hermetic temp tree.

        The scanner resolves the swarm checkout from the host filesystem, which
        does not exist on a bare CI runner, so scanning the real projects/ dir
        is not portable (it yielded an empty list and failed the old >0 assert).
        """
        import tempfile
        import parser as parser_module

        original_projects_dir = parser_module.PROJECTS_DIR
        with tempfile.TemporaryDirectory() as tmp:
            proj = os.path.join(tmp, "sampleproject")
            os.makedirs(proj)
            with open(os.path.join(proj, "README.md"), "w", encoding="utf-8") as f:
                f.write("# Sample Project\n\nA short summary line.\n")
            open(os.path.join(proj, "dev.sh"), "w").close()
            open(os.path.join(proj, "validate-release.sh"), "w").close()

            parser_module.PROJECTS_DIR = tmp
            try:
                scanned = scan_all_projects()
            finally:
                parser_module.PROJECTS_DIR = original_projects_dir

        self.assertIsInstance(scanned, list)
        self.assertEqual(len(scanned), 1)
        entry = scanned[0]
        self.assertEqual(entry["id"], "sampleproject")
        self.assertEqual(entry["title"], "Sample Project")
        self.assertTrue(entry["has_readme"])
        self.assertTrue(entry["has_dev_script"])
        self.assertTrue(entry["has_release_gate"])


if __name__ == "__main__":
    unittest.main()

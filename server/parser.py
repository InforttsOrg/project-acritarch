"""
Dynamic Project & Documentation Parser for Acritarch
Scans project submodules across inforttsOrg to index markdown docs and API routes.
"""

import os
import json
import re
from typing import Dict, Any, List, Optional

INFORTTS_ROOT = "/Users/admin/rttss-sahil/inforttsOrg"
PROJECTS_DIR = os.path.join(INFORTTS_ROOT, "projects")


def get_project_markdown(project_id: str) -> Dict[str, str]:
    """Reads available Markdown documentation for a given project."""
    docs = {}
    pdir = os.path.join(PROJECTS_DIR, project_id)
    if not os.path.isdir(pdir):
        return docs

    candidates = ["README.md", "MINDMAP.md", "task.md", "AGENTS.md", "GEMINI.md", "docs/index.md"]
    for c in candidates:
        cp = os.path.join(pdir, c)
        if os.path.isfile(cp):
            try:
                with open(cp, "r", encoding="utf-8", errors="replace") as f:
                    docs[c] = f.read()
            except Exception:
                pass
    return docs


def scan_all_projects() -> List[Dict[str, Any]]:
    """Discovers all subprojects in projects/ directory."""
    results = []
    if not os.path.isdir(PROJECTS_DIR):
        return results

    for entry in sorted(os.listdir(PROJECTS_DIR)):
        if entry.startswith("."):
            continue
        full_path = os.path.join(PROJECTS_DIR, entry)
        if os.path.isdir(full_path):
            readme_path = os.path.join(full_path, "README.md")
            has_readme = os.path.isfile(readme_path)
            title = entry
            summary = ""
            if has_readme:
                try:
                    with open(readme_path, "r", encoding="utf-8", errors="replace") as f:
                        lines = f.readlines()
                        for line in lines:
                            if line.startswith("# ") and title == entry:
                                title = line.replace("# ", "").strip()
                            elif line.strip() and not line.startswith("#") and not summary:
                                summary = line.strip()[:180]
                except Exception:
                    pass

            results.append({
                "id": entry,
                "title": title,
                "summary": summary,
                "has_readme": has_readme,
                "has_dev_script": os.path.isfile(os.path.join(full_path, "dev.sh")),
                "has_release_gate": os.path.isfile(os.path.join(full_path, "validate-release.sh"))
            })
    return results

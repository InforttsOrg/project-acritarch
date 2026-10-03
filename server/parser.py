"""
Dynamic Project & Documentation Parser for Acritarch
Scans project submodules across inforttsOrg to index markdown docs and API routes.
"""

import os
from typing import Dict, Any, List

# Candidate swarm roots, ordered by priority. The first one that actually
# contains a populated "projects/" directory wins, so the same code runs on
# the VPS master node and on developer workstations.
_ROOT_CANDIDATES = [
    os.environ.get("ACRITARCH_INFORTTS_ROOT", ""),
    "/opt/infortts",
    "/Users/admin/rttss-sahil/inforttsOrg",
]


def _resolve_infortts_root() -> str:
    for candidate in _ROOT_CANDIDATES:
        if candidate and os.path.isdir(os.path.join(candidate, "projects")):
            return candidate
    return _ROOT_CANDIDATES[1]


INFORTTS_ROOT = _resolve_infortts_root()
PROJECTS_DIR = os.path.join(INFORTTS_ROOT, "projects")

# Markdown files indexed for each project.
DOC_CANDIDATES = ["README.md", "MINDMAP.md", "task.md", "AGENTS.md", "GEMINI.md", "docs/index.md"]


def _resolve_project_dir(project_id: str) -> str:
    """Resolves a project id to its directory, refusing anything outside PROJECTS_DIR.

    Guards against path traversal (e.g. "../../etc") since project_id originates
    from an untrusted HTTP path parameter in /api/docs/{service_id}/markdown.
    """
    if not project_id or project_id in (".", "..") or os.path.isabs(project_id):
        return ""
    if os.sep in project_id or (os.altsep and os.altsep in project_id):
        return ""

    pdir = os.path.realpath(os.path.join(PROJECTS_DIR, project_id))
    root = os.path.realpath(PROJECTS_DIR)
    if pdir == root or not pdir.startswith(root + os.sep):
        return ""
    return pdir


def get_project_markdown(project_id: str) -> Dict[str, str]:
    """Reads available Markdown documentation for a given project."""
    docs = {}
    pdir = _resolve_project_dir(project_id)
    if not pdir or not os.path.isdir(pdir):
        return docs

    for c in DOC_CANDIDATES:
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

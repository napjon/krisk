import re
from pathlib import Path

import nbformat

ROOT = Path(__file__).resolve().parents[2]


def test_local_markdown_links_exist():
    documents = [ROOT / "README.md", ROOT / "CHANGELOG.md", *sorted((ROOT / "docs").glob("*.md"))]
    missing = []
    for document in documents:
        for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", document.read_text(encoding="utf-8")):
            if "://" in target or target.startswith("#"):
                continue
            path = target.split("#", 1)[0]
            if path and not (document.parent / path).resolve().exists():
                missing.append(f"{document.relative_to(ROOT)} -> {target}")
    assert not missing, "Missing documentation links:\n" + "\n".join(missing)


def test_documented_version_matches_package():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "current package version is `0.9.0`" in readme
    assert "## 0.9.0" in changelog


def test_tutorial_notebooks_are_current_and_self_contained():
    notebooks = sorted((ROOT / "notebooks").glob("*.ipynb"))
    assert len(notebooks) == 7
    for path in notebooks:
        notebook = nbformat.read(path, as_version=4)
        assert notebook.metadata["krisk"] == {
            "version": "0.9.0",
            "category": notebook.metadata["krisk"]["category"],
            "requires_server": False,
        }
        assert notebook.metadata["language_info"]["version"] == "3.11"
        sources = "\n".join(cell.source for cell in notebook.cells)
        assert "init_notebook" not in sources
        assert "stat.ubc.ca" not in sources
        for index, cell in enumerate(notebook.cells):
            if cell.cell_type == "code":
                compile(cell.source, f"{path.name}:cell-{index}", "exec")
                assert cell.execution_count is None
                assert not cell.outputs

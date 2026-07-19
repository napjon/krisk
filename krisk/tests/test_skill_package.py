import re
from pathlib import Path

import yaml

SKILL_ROOT = Path("skills/save-research-notebook")


def test_research_skill_metadata_and_references_are_valid():
    content = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", content, flags=re.DOTALL)
    assert match is not None
    frontmatter = yaml.safe_load(match.group(1))
    assert frontmatter == {
        "name": "save-research-notebook",
        "description": frontmatter["description"],
    }
    assert len(frontmatter["description"]) >= 80

    referenced = re.findall(r"\]\((references/[^)]+)\)", content)
    assert referenced
    assert all((SKILL_ROOT / relative).is_file() for relative in referenced)

    metadata = yaml.safe_load((SKILL_ROOT / "agents/openai.yaml").read_text(encoding="utf-8"))
    dependency = metadata["dependencies"]["tools"][0]
    assert dependency["value"] == "krisk"
    assert dependency["url"] == "http://127.0.0.1:8060/mcp/"

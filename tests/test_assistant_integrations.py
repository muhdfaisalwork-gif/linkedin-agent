import os
import json
import yaml
import pytest

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def test_skill_spec_format():
    skill_path = os.path.join(REPO_ROOT, "skill", "SKILL.md")
    assert os.path.exists(skill_path), f"Skill definition missing at {skill_path}"

    with open(skill_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Verify frontmatter
    assert content.startswith("---"), "SKILL.md must start with YAML frontmatter delimiter '---'"
    parts = content.split("---", 2)
    assert len(parts) >= 3, "SKILL.md must contain frontmatter enclosed by '---'"

    frontmatter = yaml.safe_load(parts[1])
    assert "name" in frontmatter
    assert frontmatter["name"] == "linkedin-nexus-agent"
    assert "description" in frontmatter
    assert "compatibility" in frontmatter

    # Verify key sections
    body = parts[2]
    assert "Humanizer" in body
    assert "Story Bank" in body
    assert "draft_linkedin_post" in body
    assert "scan_linkedin_feed" in body

def test_chatgpt_openapi_spec():
    spec_path = os.path.join(REPO_ROOT, "integrations", "chatgpt", "openapi.yaml")
    assert os.path.exists(spec_path), f"ChatGPT OpenAPI spec missing at {spec_path}"

    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    assert "openapi" in spec
    assert spec["openapi"].startswith("3.0") or spec["openapi"].startswith("3.1")
    assert "info" in spec
    assert spec["info"]["title"] == "LinkedIn Nexus Agent API"
    assert "paths" in spec
    paths = spec["paths"]
    assert "/api/posts/draft" in paths
    assert "/api/posts/humanize" in paths
    assert "/api/brain/story-bank" in paths
    assert "/api/reach/inspect" in paths

    # Verify instructions file
    instructions_path = os.path.join(REPO_ROOT, "integrations", "chatgpt", "instructions.md")
    assert os.path.exists(instructions_path)
    with open(instructions_path, "r", encoding="utf-8") as f:
        inst_text = f.read()
    assert "Custom GPT" in inst_text
    assert "82 Humanizer Rules" in inst_text

def test_gemini_function_declarations():
    decl_path = os.path.join(REPO_ROOT, "integrations", "gemini", "function_declarations.json")
    assert os.path.exists(decl_path), f"Gemini function declarations missing at {decl_path}"

    with open(decl_path, "r", encoding="utf-8") as f:
        declarations = json.load(f)

    assert isinstance(declarations, list)
    assert len(declarations) >= 5

    names = [d.get("name") for d in declarations]
    assert "draft_linkedin_post" in names
    assert "scan_linkedin_feed" in names
    assert "inspect_linkedin_url" in names
    assert "get_story_bank_receipts" in names

    for decl in declarations:
        assert "name" in decl
        assert "description" in decl
        assert "parameters" in decl
        assert decl["parameters"]["type"] == "OBJECT"

def test_install_scripts_exist():
    mcp_script = os.path.join(REPO_ROOT, "scripts", "install_mcp.py")
    skill_script = os.path.join(REPO_ROOT, "scripts", "install_skill.py")
    run_mcp = os.path.join(REPO_ROOT, "run_mcp.py")

    assert os.path.exists(mcp_script)
    assert os.path.exists(skill_script)
    assert os.path.exists(run_mcp)

    with open(run_mcp, "r", encoding="utf-8") as f:
        run_content = f.read()
    assert "run_stdio_server" in run_content

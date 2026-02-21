"""Structural tests -- verify project files, skills, and docs are well-formed."""
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
SKILLS = ROOT / "skills"
DOCS = ROOT / "docs"

# ---------------------------------------------------------------------------
# Skill structure tests
# ---------------------------------------------------------------------------

SKILL_NAMES = ["uber-polya", "uber-model", "uber-solve", "uber-interpret"]


@pytest.mark.parametrize("skill_name", SKILL_NAMES)
def test_skill_directory_exists(skill_name: str):
    skill_dir = SKILLS / skill_name
    assert skill_dir.is_dir(), f"Skill directory missing: {skill_dir}"


@pytest.mark.parametrize("skill_name", SKILL_NAMES)
def test_skill_has_skill_md(skill_name: str):
    skill_md = SKILLS / skill_name / "SKILL.md"
    assert skill_md.is_file(), f"SKILL.md missing: {skill_md}"


@pytest.mark.parametrize("skill_name", SKILL_NAMES)
def test_skill_md_has_frontmatter(skill_name: str):
    """SKILL.md must start with YAML frontmatter containing name and description."""
    skill_md = SKILLS / skill_name / "SKILL.md"
    content = skill_md.read_text()
    assert content.startswith("---"), f"SKILL.md missing YAML frontmatter: {skill_md}"

    # Find closing ---
    second_dash = content.find("---", 3)
    assert second_dash > 3, f"SKILL.md frontmatter not closed: {skill_md}"

    frontmatter = content[3:second_dash]
    assert "name:" in frontmatter, f"SKILL.md frontmatter missing 'name:': {skill_md}"
    assert "description:" in frontmatter, f"SKILL.md frontmatter missing 'description:': {skill_md}"


@pytest.mark.parametrize("skill_name", ["uber-model", "uber-solve", "uber-interpret"])
def test_skill_has_references(skill_name: str):
    ref_dir = SKILLS / skill_name / "references"
    assert ref_dir.is_dir(), f"References directory missing: {ref_dir}"
    refs = list(ref_dir.glob("*.md"))
    assert len(refs) >= 1, f"No reference files found in {ref_dir}"


# ---------------------------------------------------------------------------
# Example structure tests
# ---------------------------------------------------------------------------

EXAMPLE_DIRS = sorted(
    d.name for d in EXAMPLES.iterdir()
    if d.is_dir() and not d.name.startswith(".")
)


@pytest.mark.parametrize("example_name", EXAMPLE_DIRS)
def test_example_has_readme(example_name: str):
    readme = EXAMPLES / example_name / "README.md"
    assert readme.is_file(), f"README.md missing from example: {example_name}"


@pytest.mark.parametrize("example_name", EXAMPLE_DIRS)
def test_example_has_solver(example_name: str):
    """Each example must have at least one Python file."""
    example_dir = EXAMPLES / example_name
    py_files = list(example_dir.glob("*.py"))
    assert len(py_files) >= 1, f"No Python files in example: {example_name}"


# ---------------------------------------------------------------------------
# Documentation tests
# ---------------------------------------------------------------------------

HTML_FILES = [
    "index.html",
    "guide.html",
    "architecture.html",
    "creating-skills.html",
    "manifesto.html",
    "getting-started.html",
    "milking-cows-walkthrough.html",
    "inspector-assignment-walkthrough.html",
]


@pytest.mark.parametrize("html_file", HTML_FILES)
def test_html_file_exists(html_file: str):
    path = DOCS / html_file
    assert path.is_file(), f"HTML doc missing: {path}"


NAV_PAGES = [
    "architecture.html",
    "creating-skills.html",
    "manifesto.html",
    "getting-started.html",
    "milking-cows-walkthrough.html",
    "inspector-assignment-walkthrough.html",
    "index.html",
]


@pytest.mark.parametrize("html_file", NAV_PAGES)
def test_html_has_standard_nav(html_file: str):
    """All pages with nav should have the 4 standard nav links."""
    content = (DOCS / html_file).read_text()
    assert "guide.html" in content, f"Missing Docs link in {html_file}"
    assert "getting-started.html" in content, f"Missing Tutorial link in {html_file}"
    assert "manifesto.html" in content, f"Missing Manifesto link in {html_file}"
    assert "github.com/agtm1199/uber-polya" in content, f"Missing GitHub link in {html_file}"


@pytest.mark.parametrize("html_file", NAV_PAGES)
def test_html_has_no_footer_nav(html_file: str):
    """Footer should not contain navigation links (removed in v0.2.0)."""
    content = (DOCS / html_file).read_text()
    # Find footer section
    footer_match = re.search(r"<footer>(.*?)</footer>", content, re.DOTALL)
    if footer_match:
        footer = footer_match.group(1)
        assert "footer-links" not in footer or "<ul" not in footer, (
            f"Footer still contains nav links in {html_file}"
        )


# ---------------------------------------------------------------------------
# Root file tests
# ---------------------------------------------------------------------------

ROOT_FILES = ["README.md", "CHANGELOG.md", "LICENSE", "CONTRIBUTING.md", "install.sh"]


@pytest.mark.parametrize("filename", ROOT_FILES)
def test_root_file_exists(filename: str):
    path = ROOT / filename
    assert path.is_file(), f"Root file missing: {filename}"


def test_install_script_is_bash():
    content = (ROOT / "install.sh").read_text()
    assert content.startswith("#!/bin/bash"), "install.sh missing bash shebang"


def test_readme_mentions_uber_polya_as_primary():
    """README should present /uber-polya as the primary entry point."""
    content = (ROOT / "README.md").read_text()
    assert "/uber-polya" in content
    # Quick Start should use /uber-polya, not /uber-model
    quick_start_idx = content.find("## Quick Start")
    assert quick_start_idx > 0
    quick_start_section = content[quick_start_idx:quick_start_idx + 500]
    assert "/uber-polya" in quick_start_section

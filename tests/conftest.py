"""Shared fixtures for uber-polya tests."""
from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"
SKILLS = ROOT / "skills"
DOCS = ROOT / "docs"


@pytest.fixture
def root():
    return ROOT


@pytest.fixture
def examples_dir():
    return EXAMPLES


@pytest.fixture
def skills_dir():
    return SKILLS


@pytest.fixture
def docs_dir():
    return DOCS

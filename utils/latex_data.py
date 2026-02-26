#!/usr/bin/env python3
"""Data classes for the LaTeX/PDF report pipeline.

Mirrors the three artifact schemas from the uber-polya orchestrator:
  Artifact 1: Formal Model   (Phase A → Phase B)
  Artifact 2: Solution Report (Phase B → Phase C)
  Artifact 3: Interpretation Report (Phase C → final deliverable)

These are the structured intermediate representation consumed by
``LatexRenderer`` to produce ``.tex`` and ``.pdf`` output.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


# ── Phase A: Formal Model components ─────────────────────────────────

@dataclass(frozen=True)
class Variable:
    """A decision / free variable in the formal model."""
    name: str          # LaTeX symbol, e.g. "x_{ij}"
    meaning: str       # plain-English description
    type_range: str    # e.g. "binary", "\\mathbb{R}_{\\ge 0}"


@dataclass(frozen=True)
class MappingRow:
    """One row of the real-world ↔ math mapping table."""
    real_world: str
    math_object: str


@dataclass(frozen=True)
class Constraint:
    """A numbered constraint with its real-world origin."""
    number: int
    formal: str        # LaTeX math expression
    origin: str        # which real-world condition


@dataclass
class FormalModel:
    """Artifact 1 – produced by Phase A (uber-model)."""
    problem_type: str                  # "Find" or "Prove"
    domain: str                        # e.g. "Combinatorial Optimization"
    named_problem: str | None          # e.g. "Minimum Weight Bipartite Matching"
    universe: list[str]                # set definitions
    variables: list[Variable]
    structure: str                     # core mathematical object definition
    mapping: list[MappingRow]
    constraints: list[Constraint]
    objective: str | None              # for Find problems
    claim: str | None                  # for Prove problems
    suggested_approach: str
    complexity_class: str
    available_tools: list[str] = field(default_factory=list)


# ── Phase B: Solution Report components ──────────────────────────────

@dataclass(frozen=True)
class VerificationCheck:
    """One independent verification check."""
    name: str
    passed: bool
    value: str         # human-readable result detail


@dataclass
class SolutionReport:
    """Artifact 2 – produced by Phase B (uber-solve)."""
    answer: str                        # the solution value / proof / count
    objective_value: float | None
    is_optimal: bool
    is_feasible: bool
    algorithm: str                     # name of algorithm used
    complexity: str                    # e.g. "O(n^3)"
    time_seconds: float
    certificate: str | None            # optimality proof description
    details: str                       # free-form solution details (markdown)
    verification: list[VerificationCheck] = field(default_factory=list)
    solver_code: str | None = None     # Python source (for appendix in Both mode)


# ── Phase C: Interpretation Report components ────────────────────────

@dataclass(frozen=True)
class SensitivityRow:
    """One row of the sensitivity analysis table."""
    parameter: str
    current: str
    change: str
    new_objective: str
    classification: str   # "robust" | "sensitive" | "critical"


@dataclass(frozen=True)
class Figure:
    """A visualization figure to embed in the report."""
    path: Path
    caption: str


@dataclass
class InterpretationReport:
    """Artifact 3 – produced by Phase C (uber-interpret)."""
    question: str                      # one sentence: what were we trying to do?
    answer: str                        # one sentence: bottom line in plain language
    what_this_means: str               # 2-3 paragraphs translating the solution
    sensitivity: list[SensitivityRow] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)
    limitations: list[str] = field(default_factory=list)
    figures: list[Figure] = field(default_factory=list)


# ── Report configuration ─────────────────────────────────────────────

@dataclass
class ReportConfig:
    """Settings for report generation."""
    title: str
    output_dir: Path
    include_code: bool = False         # include Python listing in appendix
    date: str | None = None            # defaults to today
    author: str = "uber-polya"
    pipeline_mode: str = "Full Pipeline"

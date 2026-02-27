"""Data structures for First Proof challenge submission."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class FirstProofProblem:
    """A single First Proof problem with solution."""
    number: int
    title: str
    statement: str  # Raw LaTeX for problem statement
    solution: str   # Raw LaTeX for solution body
    confidence: str  # HIGH / MEDIUM / LOW
    confidence_note: str  # Brief justification
    references: list[str] = field(default_factory=list)  # \bibitem entries
    layman_explanation: str = ""  # Plain-language explanation for layman


@dataclass
class FirstProofDocument:
    """The complete First Proof submission document."""
    problems: list[FirstProofProblem] = field(default_factory=list)

    def sorted_problems(self) -> list[FirstProofProblem]:
        """Return problems sorted by number."""
        return sorted(self.problems, key=lambda p: p.number)

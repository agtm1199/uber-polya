#!/usr/bin/env python3
"""Generate LaTeX source for First Proof submission from content files.

Each content file (content/problemNN_*.tex) uses markers:
    [problem statement]
    %%% SOLUTION %%%
    [solution body]
    %%% REFERENCES %%%
    \\bibitem{key} text...
    %%% HSEXPLAIN %%%
    [high school explanation]

The confidence line is extracted from the solution body:
    \\paragraph{Confidence.} HIGH/MEDIUM/LOW -- justification
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from data import FirstProofProblem, FirstProofDocument

CONTENT_DIR = Path(__file__).parent / "content"
TEMPLATE_DIR = Path(__file__).parent / "templates"
OUTPUT_DIR = Path(__file__).parent / "output"


def parse_content_file(path: Path) -> FirstProofProblem:
    """Parse a content file into a FirstProofProblem."""
    text = path.read_text()

    # Extract problem number from filename: problemNN_*.tex
    match = re.match(r"problem(\d+)_", path.name)
    if not match:
        raise ValueError(f"Cannot extract problem number from {path.name}")
    number = int(match.group(1))

    # Split on markers
    parts = re.split(r"%%% (SOLUTION|REFERENCES|HSEXPLAIN) %%%", text)

    statement = parts[0].strip()
    solution = ""
    references_text = ""
    layman_explanation = ""

    i = 1
    while i < len(parts):
        marker = parts[i]
        content = parts[i + 1].strip() if i + 1 < len(parts) else ""
        if marker == "SOLUTION":
            solution = content
        elif marker == "REFERENCES":
            references_text = content
        elif marker == "HSEXPLAIN":
            layman_explanation = content
        i += 2

    # Extract confidence from solution body
    confidence = "MEDIUM"
    confidence_note = "See solution for details."
    conf_match = re.search(
        r"\\paragraph\{Confidence\.\}\s*(HIGH|MEDIUM|LOW)(?:-(\w+))?\s*(?:--|---)\s*(.+?)(?:\n|$)",
        solution,
    )
    if conf_match:
        confidence = conf_match.group(1)
        if conf_match.group(2):
            confidence = f"{confidence}-{conf_match.group(2)}"
        confidence_note = conf_match.group(3).strip()
        # Remove the confidence line from solution body (it'll be added by template)
        solution = re.sub(
            r"\\paragraph\{Confidence\.\}.*?(?:\n|$)", "", solution
        ).strip()

    # Extract title from first line if it starts with % Title:
    title = f"Problem {number}"
    title_match = re.match(r"^%\s*Title:\s*(.+)$", text, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()
        statement = re.sub(r"^%\s*Title:.*\n", "", statement).strip()

    # Parse references
    references = []
    if references_text:
        for line in references_text.split("\n"):
            line = line.strip()
            if line.startswith("\\bibitem"):
                references.append(line)
            elif references and not line.startswith("%"):
                # Continuation of previous bibitem
                references[-1] += " " + line

    return FirstProofProblem(
        number=number,
        title=title,
        statement=statement,
        solution=solution,
        confidence=confidence,
        confidence_note=confidence_note,
        references=references,
        layman_explanation=layman_explanation,
    )


def generate() -> Path:
    """Generate the complete LaTeX file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Parse all content files
    doc = FirstProofDocument()
    content_files = sorted(CONTENT_DIR.glob("problem*.tex"))

    if not content_files:
        print("No content files found in", CONTENT_DIR)
        sys.exit(1)

    for path in content_files:
        print(f"  Parsing {path.name}...")
        problem = parse_content_file(path)
        doc.problems.append(problem)

    print(f"  Parsed {len(doc.problems)} problems")

    # Render template
    env = Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
    )

    template = env.get_template("report.tex.j2")
    tex = template.render(problems=doc.sorted_problems())

    output_path = OUTPUT_DIR / "firstproof.tex"
    output_path.write_text(tex)
    print(f"  Written to {output_path}")
    return output_path


if __name__ == "__main__":
    generate()

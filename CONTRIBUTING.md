# Contributing to uber-polya

Thank you for your interest in improving uber-polya. This project welcomes contributions of all kinds: new heuristics, additional structures, algorithm entries, worked examples, and skill improvements.

## Ways to Contribute

### 1. Add to the Reference Catalogs

The reference catalogs are the knowledge backbone of the skills. To add an entry:

**Heuristics** (`skills/uber-model/references/heuristics.md`):
- Follow the existing format: H-number, name, "When to use", "Socratic questions", "DM application"
- Heuristics should be general enough to apply across multiple problem types
- Include concrete Socratic questions (not directives)

**DM Structures** (`skills/uber-model/references/structures.md`):
- Follow the format: Definition, Indicators, Template, Examples, Key Problems
- Indicators should be phrases a non-mathematician might use to describe a problem
- Include 2-3 real-world-to-math mapping examples

**Algorithms** (`skills/uber-solve/references/algorithms.md`):
- Follow the format: Problem, Complexity, Library, Guarantee, Code snippet, When to use
- Always include the correctness guarantee (exact/approximate/heuristic)
- Include a working Python code snippet using an established library

**Solver Libraries** (`skills/uber-solve/references/solvers.md`):
- Add new libraries with: What it solves, Installation, Key APIs, Performance notes

### 2. Submit Worked Examples

A good example demonstrates all three skills on a real problem. Include:

1. **README.md** with problem description and walkthrough
2. **Solver script** (.py) with:
   - `Instance` and `Solution` dataclasses
   - `solve()` function with timing
   - `verify()` function independent of the solver
   - Test cases
3. **Visualization script** (.py) with matplotlib charts
4. **Input/output files** if applicable

Place in `examples/<problem-name>/` and add an entry to the examples table in the root README.

### 3. Contribute a New Domain

uber-polya is designed for modular expansion. To add a new computational domain (e.g., continuous optimization, statistical inference, machine learning):

**Reference files to create:**
- `skills/uber-solve/references/algorithms-<domain>.md` -- Algorithm catalog following the existing format (Problem, Complexity, Library, Guarantee, Code snippet, When to use)
- `skills/uber-solve/references/solvers-<domain>.md` -- Solver library guide (What it solves, Installation, Key APIs, Performance notes)
- Entries in `skills/uber-model/references/structures.md` -- New mathematical structures with real-world indicators

**SKILL.md sections to add:**
- A new "Protocol: <Domain>" section in `uber-solve/SKILL.md`
- New entries in the Phase 0 classification table
- New interpretation patterns in `uber-interpret/references/interpretation-patterns.md`
- New visualization templates in `uber-interpret/references/visualization.md`

**Requirements for a new domain contribution:**
- At least 10 algorithms with complexity and library references
- At least 1 solver library with installation and API guide
- At least 3 mathematical structures with real-world indicator phrases
- At least 1 worked example demonstrating the full trilogy pipeline
- Verification paradigm documented (how are solutions verified in this domain?)

See [Architecture: Expansion Architecture](docs/architecture.md#expansion-architecture) for the full design.

### 4. Improve Skill Instructions

The SKILL.md files are the core of each skill. Improvements could include:
- Better phase transitions or gate questions
- New error recovery strategies
- Improved output format templates
- Additional problem-specific protocols (in uber-solve)

## SKILL.md Style Guide

### Frontmatter

```yaml
---
name: skill-name
description: >
  Use when the user wants to "trigger phrase 1", "trigger phrase 2", ...
---
```

The description field lists trigger phrases that Claude uses for skill matching.

### Phase Structure

Each skill follows a phase-based progression:

```markdown
## Phase N: Phase Name

*Polya quote or motivation*

### Step 1: Step name
[Instructions]

### Step 2: Step name
[Instructions]

### Phase N Gate
[AskUserQuestion to confirm before proceeding]
```

### Conventions

- Use AskUserQuestion at phase transitions (gates) to confirm understanding
- Reference files with `Read references/filename.md` instructions
- Use structured output templates (markdown tables, code blocks) for consistency
- Include error recovery sections for each phase
- Cross-reference other skills with `/uber-model`, `/uber-solve`, `/uber-interpret` notation

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b add-algorithm-ford-fulkerson`)
3. Make your changes following the style guide above
4. Test by copying your modified skill to `~/.claude/skills/` and invoking it
5. Submit a PR with a description of what you added and why

## Testing Skills

Skills are tested through conversation, not unit tests:

1. Copy the modified skill to `~/.claude/skills/`
2. Open Claude Code
3. Invoke the skill with a relevant problem
4. Verify each phase produces the expected output format
5. Verify reference files are read and applied correctly
6. Test with at least 2 problem types (one simple, one complex)

## Code of Conduct

Be respectful, constructive, and focused on improving the project. Mathematical rigor and pedagogical clarity are equally valued.

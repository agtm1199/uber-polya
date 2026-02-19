# Creating Your Own Skills

How to build Claude Code skills using patterns from the uber-polya project.

## What Is a Claude Code Skill?

A skill is a markdown file that specifies Claude's behavior when invoked as a slash command. Skills live in `.claude/skills/` -- either globally at `~/.claude/skills/` (available in every project) or locally at `./.claude/skills/` (scoped to one project). When a user types `/skill-name` or describes a task matching the skill's trigger phrases, Claude activates the skill and follows its instructions.

Skills are not code. They are structured natural-language specifications -- phase-by-phase workflows with steps, verification gates, output templates, and reference catalogs. Claude reads the skill and follows it as a behavioral contract.

## SKILL.md Anatomy

Every skill lives in a directory with a `SKILL.md` file and an optional `references/` subdirectory.

### YAML Frontmatter

```yaml
---
name: my-skill
description: >
  Use when the user wants to "do X", "solve Y", "analyze Z",
  or needs help with [domain]. Include trigger phrases that
  Claude uses to auto-suggest this skill.
---
```

The `name` field becomes the slash command: `/my-skill`. The `description` field lists natural-language trigger phrases. Claude uses these to suggest the skill when the user's request matches, even without the slash command.

### Body Structure

The body follows a consistent pattern across uber-polya's three skills:

1. **Title and role statement** -- a one-line identity for Claude ("You are a Socratic problem-modeling guide")
2. **Core principles** -- 3-6 behavioral rules that govern all phases
3. **Skill scope** -- what this skill does and does not cover
4. **Reference file listing** -- paths and descriptions of reference files, with instructions on when to read them
5. **Phases** -- the sequential workflow, each with steps, Socratic questions, output templates, and gates
6. **Error recovery** -- what to do when a phase fails or the user expresses doubt
7. **Output format summary** -- a quick-reference list of all artifacts the skill produces

### Reference Files

Reference files are markdown catalogs that Claude reads on demand using the Read tool. They live in `references/` alongside the SKILL.md:

```
.claude/skills/my-skill/
  SKILL.md
  references/
    catalog.md
    patterns.md
```

In the SKILL.md body, instruct Claude when to read them:

```markdown
## Reference Files

- `references/catalog.md` -- 40 entries with definitions and examples
- `references/patterns.md` -- Domain-specific application patterns

Read both reference files at the start of Phase 2.
```

Claude will use the Read tool to load these files when it reaches the specified phase. This keeps the skill lightweight at invocation time while providing deep domain knowledge when needed.

## Skill Directory Structure

A complete skill directory:

```
.claude/skills/my-skill/
  SKILL.md              # The behavior specification
  references/
    catalog.md          # Domain knowledge catalog
    patterns.md         # Application patterns
```

For uber-polya, each skill has exactly one SKILL.md and two reference files:

```
skills/
  uber-model/
    SKILL.md                        # 370 lines, 4 phases
    references/
      heuristics.md                 # 17 Polya heuristics
      structures.md              # 32 DM structures
  uber-solve/
    SKILL.md                        # 465 lines, 5 phases
    references/
      algorithms.md                 # 86 algorithms
      solvers.md                    # Python solver ecosystem
  uber-interpret/
    SKILL.md                        # 490 lines, 6 phases
    references/
      interpretation-patterns.md    # Domain translation patterns
      visualization.md              # Chart templates
```

## Key Patterns Used in uber-polya

### Phase gates

Phase gates are checkpoints where the skill pauses and asks the user to confirm understanding before proceeding. They use AskUserQuestion with multiple-choice options:

```markdown
### Phase 1 Gate

Present your understanding back to the user in this structured format:

[output template]

Use AskUserQuestion to confirm:

  Does this capture your problem correctly?
    (a) Yes, that's right
    (b) Mostly, but [user corrects]
    (c) No, let me restate it

Do NOT proceed to Phase 2 until the user confirms understanding.
```

Gates serve two purposes: they ensure the skill stays aligned with the user's intent, and they embody Polya's principle that the user should do the thinking. uber-model has gates after Phase 1 (problem understanding) and Phase 2 (model selection). uber-solve has a gate after Phase 0 (problem classification). uber-interpret has a gate in Phase 0 (audience identification).

### Reference reading

Reference files are read at specific phases, not at skill invocation. This pattern keeps initial response time fast and loads domain knowledge only when relevant:

```markdown
### Step 1: Read references

Read both reference files:
- `references/algorithms.md` -- find the specific algorithm entry
- `references/solvers.md` -- confirm the solver library is available
```

Claude interprets this as an instruction to use its Read tool on the file paths relative to the SKILL.md location.

### Structured output templates

Every phase produces output in a consistent markdown format. Templates use headers, tables, and code blocks:

```markdown
## Formal Model

**Domain**: [Graph Theory / Combinatorics / ...]
**Universe**: [The set of objects under consideration]
**Variables**:
  - [symbol]: [meaning] [type/range]
**Structure**: [The core mathematical object]
**Mapping**:
  | Real-World Concept | Mathematical Object |
  |---|---|
  | [concept] | [math object] |
**Constraints**:
  1. [First formal constraint]
  2. [Second formal constraint]
**Objective**: [Minimize/Maximize/Find/Count]: [formal expression]
```

Consistent templates make outputs machine-parseable and allow downstream skills to extract what they need. uber-solve can parse uber-model's Formal Model block because the format is specified, not improvised.

### Error recovery sections

Each skill ends with an error recovery section that handles failures without abandoning the workflow:

```markdown
## Error Recovery

If at any point the model feels wrong or the user expresses doubt:

1. Don't force it. Acknowledge the discomfort.
2. Loop back to the earliest phase where the issue originated.
3. Try Polya's "Could you restate the problem?" heuristic.
4. Try "Could you solve a part of the problem?" to find the trouble.
5. Try a tiny concrete example to build intuition.
```

This pattern prevents Claude from getting stuck in a broken phase and models the cyclic nature of real problem-solving.

### Cross-skill references

Skills mention other skills as next steps, creating a natural pipeline without hard dependencies:

```markdown
## Next Steps (for /uber-solve)

**Suggested approach**: [algorithm/method]
**Complexity class**: [P / NP-hard / etc.]
**Available tools**: [solver names, libraries]
```

uber-model's Phase 4 bridges to uber-solve. uber-interpret's error recovery loops back to uber-model. This keeps each skill self-contained (you can use uber-solve without uber-model) while enabling a complete pipeline.

## How to Test

1. Copy your skill directory to `~/.claude/skills/` for global access or `.claude/skills/` in any project for local access.

2. Open Claude Code and invoke the skill with a test problem:

   ```
   /my-skill Here is a sample problem for testing.
   ```

3. Walk through the full workflow and verify:
   - Each phase produces the expected output format
   - Phase gates pause and ask for confirmation
   - Reference files are read at the correct phase
   - Error recovery activates when you express doubt
   - Cross-skill references point to valid skill names

4. Test with problems at different difficulty levels: a trivial case (to verify fast-tracking works), a standard case (to verify the full workflow), and an ambiguous or vague case (to verify Socratic questioning depth).

5. Verify that the skill's description triggers auto-suggestion by describing a task in the trigger phrases without using the slash command.

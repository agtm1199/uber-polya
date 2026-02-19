# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-02-18

### Changed

- Rebranded from dm-polya to **uber-polya** -- universal problem-solving framework
- Renamed skills: dm-model → uber-model, dm-solve → uber-solve, dm-interpret → uber-interpret
- Reframed documentation from "discrete mathematics" to universal scope with modular expansion
- Updated all SKILL.md titles, descriptions, and trigger phrases for universal coverage
- Added expansion roadmap (11 planned domains) to README
- Added "Why Start With Discrete Mathematics?" and "Expansion Architecture" to architecture docs
- Added "Contribute a New Domain" guide to CONTRIBUTING.md

## [0.1.0] - 2026-02-18

### Added

- `/uber-model` skill: Socratic modeling guide with 4 Polya phases
  - 17 Polya heuristics adapted for discrete mathematics
  - 32 DM structures across 8 domains with real-world pattern matching
- `/uber-solve` skill: Algorithm selection and verified solver engineering
  - 85+ algorithms with complexity, solver libraries, and implementation patterns
  - Python solver ecosystem guide (NetworkX, PuLP, Z3, SymPy, SciPy, OR-Tools)
- `/uber-interpret` skill: Solution interpretation for stakeholders
  - Domain-specific translation patterns (math to real-world)
  - Visualization guide with 14+ chart types and matplotlib templates
- Two worked examples:
  - **Milking Cows** (USACO): interval merging, O(N log N), with brute-force verification
  - **Inspector Assignment**: bipartite ILP with sensitivity analysis and stakeholder visualizations
- Installation script with global/project-level options
- Architecture documentation and tutorials

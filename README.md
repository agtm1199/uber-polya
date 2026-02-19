# uber-polya

**A universal problem-solving engine for Claude Code, inspired by George Polya's "How to Solve It."**

Three skills that turn any computational problem into a formal model, solve it with the right algorithm, and translate the result into actionable insight -- through Socratic dialogue.

## The Trilogy

```
/uber-model          /uber-solve           /uber-interpret
"What IS the         "What is the          "What does it
 problem?"            ANSWER?"              MEAN?"

 Real-world   -->    Formal Model   -->    Verified      -->   Actionable
 problem             (math)                Solution            Insight

 Polya Phase         Polya Phase           Polya Phase
 1-2: Understand     3: Execute            4: Look Back
 & Plan
```

Each skill's output feeds the next. Together they implement Polya's complete problem-solving cycle -- a universal methodology that works across every mathematical domain.

## The Vision

Polya's method is not limited to any single branch of mathematics. It applies to discrete optimization, continuous calculus, statistical inference, machine learning, simulation, and beyond. uber-polya implements this universal methodology as a modular, extensible framework.

**Currently shipped**: Discrete mathematics (86+ algorithms, 32 structures, 6 solver libraries) -- the domain with the most mature solver ecosystem and cleanest complexity theory.

**Expansion planned**: Each new domain plugs in as additional reference files and protocol sections, without changing the core Polya workflow.

## What Are Claude Code Skills?

Skills are markdown behavior specifications that live in `.claude/skills/` and activate as slash commands. No code to install, no dependencies to manage -- you copy directories and they work. Each skill guides Claude through a structured workflow with phases, verification gates, and reference catalogs.

## Installation

```bash
git clone https://github.com/your-username/uber-polya.git
cd uber-polya
bash install.sh
```

The installer asks whether to install globally (`~/.claude/skills/`, available in all projects) or locally (`./.claude/skills/`, current project only).

### Manual installation

```bash
cp -r skills/uber-model  ~/.claude/skills/
cp -r skills/uber-solve  ~/.claude/skills/
cp -r skills/uber-interpret ~/.claude/skills/
```

## Quick Start

Open Claude Code and type:

```
/uber-model I need to schedule 4 exams into time slots so no student
has two exams at the same time.
```

Claude guides you through Polya's phases:
1. **Understand** -- "What is the unknown? What are the constraints?"
2. **Plan** -- "This maps to graph coloring on a conflict graph."
3. **Execute** -- Builds the formal model with variables, constraints, and objective.
4. **Look Back** -- Tests with a small example, notes generalizations.

Then continue with `/uber-solve` (verified solver) and `/uber-interpret` (visualization + recommendations).

## What's Inside

### Skills (9 files, 5,220 lines)

| Skill | Files | Purpose |
|-------|-------|---------|
| `uber-model` | SKILL.md + 2 references | Socratic modeling guide with 4 Polya phases |
| `uber-solve` | SKILL.md + 2 references | Algorithm selection + verified solver engineering |
| `uber-interpret` | SKILL.md + 2 references | Solution interpretation for stakeholders |

### Reference Catalogs

| Catalog | Skill | Entries |
|---------|-------|---------|
| Polya's Heuristics | uber-model | 17 heuristics with Socratic questions |
| Structure Catalog | uber-model | 32 structures across 8 mathematical domains |
| Algorithm Catalog | uber-solve | 86+ algorithms with complexity and Python libraries |
| Solver Ecosystem | uber-solve | 6 Python solver libraries (NetworkX, PuLP, Z3, SymPy, SciPy, OR-Tools) |
| Interpretation Patterns | uber-interpret | Domain-specific math-to-reality translation |
| Visualization Guide | uber-interpret | 14+ chart types with matplotlib templates |

### Domains Currently Covered

Graph Theory, Combinatorics, Set Theory, Logic, Number Theory, Relations & Orders, Optimization, Discrete Probability.

## Roadmap

The uber-polya framework is designed for modular expansion. Each domain adds new reference files and protocol sections to the existing skills, without changing the core Polya workflow.

| Domain | Status | What It Adds |
|--------|--------|--------------|
| Discrete Mathematics | Shipped | 86+ algorithms, 32 structures, 6 solver libraries |
| Continuous Optimization | Planned | Gradient descent, convex optimization, Newton's method, cvxpy/scipy |
| Statistical Inference | Planned | Hypothesis testing, regression, Bayesian methods, statsmodels/pymc |
| Machine Learning | Planned | Classification, clustering, dimensionality reduction, scikit-learn |
| Differential Equations | Planned | ODE/PDE solvers, numerical integration, scipy.integrate |
| Simulation | Planned | Monte Carlo, discrete-event, agent-based, SimPy/Mesa |
| Signal Processing | Planned | FFT, filtering, spectral analysis, scipy.signal |
| Game Theory | Planned | Nash equilibrium, mechanism design, nashpy |
| Control Theory | Planned | PID, optimal control, Kalman filtering |
| Time Series | Planned | ARIMA, forecasting, anomaly detection, statsmodels |
| Information Theory | Planned | Entropy, mutual information, compression bounds |

Contributions for any planned domain are welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Examples

Two fully worked examples demonstrate the complete trilogy pipeline:

| Example | Domain | Algorithm | Key Concepts |
|---------|--------|-----------|--------------|
| [Milking Cows](examples/milking-cows/) | Interval merging | Sort + sweep, O(N log N) | Greedy algorithms, brute-force verification |
| [Inspector Assignment](examples/inspector-assignment/) | Bipartite ILP | PuLP/CBC solver | LP relaxation, sensitivity analysis, stakeholder viz |

Each example includes the solver script, visualizations, and a tutorial walkthrough.

## Requirements

- **Claude Code** (Anthropic's CLI) -- the runtime for skills
- **Python 3.10+** -- for running generated solver code

Optional Python packages (installed as needed by `/uber-solve`):

```bash
pip install networkx pulp z3-solver sympy scipy matplotlib numpy
```

## Documentation

- [Architecture](docs/architecture.md) -- How Polya's method maps to the trilogy
- [Getting Started Tutorial](docs/tutorials/getting-started.md) -- Your first problem
- [Milking Cows Walkthrough](docs/tutorials/milking-cows-walkthrough.md) -- Interval merging example
- [Inspector Assignment Walkthrough](docs/tutorials/inspector-assignment-walkthrough.md) -- ILP example
- [Creating Your Own Skills](docs/creating-skills.md) -- Build on this framework

## Design Principles

1. **Socratic, not didactic.** Claude asks questions that could have occurred to the user. Never lectures.
2. **Verify everything.** Every solution includes independent verification -- brute-force cross-check, LP relaxation bounds, or constraint-by-constraint feasibility.
3. **Right tool for the job.** Algorithm selection based on problem class and instance size, not one-size-fits-all.
4. **Audience adaptation.** Results presented differently for technical, decision-maker, domain expert, and general audiences.
5. **Knowledge transfer.** Every problem teaches a reusable modeling pattern.
6. **Modular expansion.** New domains plug in as reference files without changing the core Polya workflow.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to:
- Add heuristics, structures, or algorithms to the reference catalogs
- Contribute new mathematical domains
- Submit new worked examples

## License

[MIT](LICENSE)

## Acknowledgments

George Polya, *How to Solve It* (1945). The heuristic framework, Socratic questioning methodology, and four-phase problem-solving cycle that underpin this project are adapted from his work.

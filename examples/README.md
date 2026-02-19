# uber-polya Examples

These examples demonstrate the complete uber-polya trilogy pipeline:
**Model** (formalize the problem), **Solve** (compute the answer), **Interpret** (explain the results).

## Examples

| Name | Domain | Algorithm | Key Concepts |
|------|--------|-----------|--------------|
| [milking-cows](milking-cows/) | Interval scheduling | Greedy sweep | Interval merging, brute-force verification |
| [inspector-assignment](inspector-assignment/) | Resource allocation | Integer Linear Programming | Bipartite matching, LP relaxation, sensitivity analysis |

Each example includes solver code, visualization scripts, and sample data.
Detailed walkthroughs are in [docs/tutorials/](../docs/tutorials/).

## Requirements

Base (all examples):

```bash
pip install matplotlib numpy
```

Inspector assignment (ILP solver):

```bash
pip install pulp
```

## Note on Visualizations

Visualization outputs (`.png` files) are not committed to the repository.
Run the visualization scripts in each example directory to generate them.

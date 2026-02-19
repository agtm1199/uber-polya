# Milking Cows

## Problem

Farmer John's cows are milked by N farmers at various overlapping intervals.
Find the longest continuous milking period and the longest idle gap between
milking periods.

**Source**: USACO Training Program, Section 1.4 ("milk2")

## Files

| File | Description |
|------|-------------|
| `milk2.py` | Full solver with independent brute-force verification + 6 test cases |
| `milk2_usaco.py` | Minimal USACO submission format |
| `milk2_viz.py` | Generates 2 charts: timeline and algorithm visualization |
| `milk2.in` | Sample input (3 intervals) |
| `milk2.out` | Expected output |

## Quick Run

```bash
python3 milk2.py          # Solve, verify, run test cases
python3 milk2_viz.py      # Generate timeline and algorithm visualizations
```

## Expected Output

```
ANSWER: 900 300
```

Longest continuous milking = 900 seconds, longest idle gap = 300 seconds.

## Algorithm

1. **Sort** intervals by start time.
2. **Sweep** left-to-right, merging overlapping intervals (merge iff `next.start <= current.end`).
3. **Scan** merged intervals for the maximum duration and maximum gap.

**Complexity**: O(N log N) time, O(N) space.

## Key Concepts

- **Interval merging** -- the core greedy technique for collapsing overlapping ranges
- **Greedy sweep** -- single left-to-right pass after sorting
- **Independent verification** -- brute-force timeline array confirms the sweep result

## Full Tutorial

See [docs/tutorials/milking-cows-walkthrough.md](../../docs/tutorials/milking-cows-walkthrough.md)
for a detailed step-by-step walkthrough.

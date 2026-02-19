# Milking Cows -- Full Walkthrough

A complete walkthrough of the USACO "Milking Cows" problem (milk2), demonstrating all three uber-polya skills from problem statement to actionable insight.

**Runnable code**: `examples/milking-cows/`

> **Note**: The skill outputs shown below are representative of what Claude produces. Exact wording, formatting, and detail level will vary between runs.

---

## The Problem

N farmers milk cows during various time intervals throughout the day. Given N intervals `[start, end)`, find:

1. The **longest continuous period** during which at least one farmer is milking
2. The **longest idle gap** between milking periods (where no one is milking)

**Sample input**: 3 intervals -- `[300, 1000)`, `[700, 1200)`, `[1500, 2100)`

---

## Phase 1: /uber-model

```
/uber-model 3 farmers milk cows at different times: Farmer 1 from second 300
to 1000, Farmer 2 from 700 to 1200, Farmer 3 from 1500 to 2100. I need to
find the longest stretch where at least one farmer is milking, and the
longest gap where nobody is milking.
```

Claude works through Polya's understanding and planning phases. Representative output:

### Problem Understanding

> **Problem Type**: Problem to Find
> **Unknown**: Two values -- (1) longest continuous milking period, (2) longest idle gap
> **Data**: N intervals, each with integer start and end times. Milking occurs during `[start, end)` (half-open).
> **Conditions**:
>   1. Milking is continuous if intervals overlap or touch: `start_next <= end_current`
>   2. A gap exists between consecutive non-overlapping merged intervals
>   3. Idle gaps only count between the first and last milking times (not before or after)
> **Notation**: Let I = {[s_1, e_1), [s_2, e_2), ..., [s_N, e_N)} be the set of milking intervals.

### Structure Recognition

> **Structure**: Interval merging on the real line
>
> This maps to a classic pattern: given a set of intervals, merge all overlapping or touching intervals into maximal non-overlapping intervals, then scan the merged result.
>
> | Real-World Concept | Mathematical Object |
> |---|---|
> | Farmer's milking shift | Half-open interval [s, e) |
> | "At least one farmer milking" | Union of intervals |
> | Continuous milking period | Maximal merged interval |
> | Idle gap | Distance between consecutive merged intervals |

### Formal Model

> **Domain**: Optimization (interval geometry)
> **Universe**: Time axis (non-negative integers)
> **Variables**: Merged interval set M = {[m_1, m_1'), [m_2, m_2'), ...}
> **Objective**:
>   - Longest milking = max(m_i' - m_i) over all merged intervals
>   - Longest idle = max(m_{i+1} - m_i') over consecutive merged intervals
>
> **Next Steps (for /uber-solve)**: Sort intervals by start time, merge in a linear sweep. O(N log N) time, O(N) space. Not NP-hard -- this is a greedy algorithm with a clean polynomial solution.

---

## Phase 2: /uber-solve

```
/uber-solve
```

Claude classifies the problem, selects the algorithm, writes a verified solver, and runs it.

### Problem Classification

> **Named Problem**: Interval merging (sweep line)
> **Complexity Class**: O(N log N) -- dominated by the sort
> **Instance Size**: N = 3
> **Solution Strategy**: Exact polynomial (sort + linear sweep)
> **Correctness Guarantee**: Deterministic, examines every interval exactly once

### The Algorithm

The solver follows three steps. Here is the core logic (from `examples/milking-cows/milk2.py`):

```python
# Step 1: Sort by start time
sorted_intervals = sorted(intervals)

# Step 2: Merge overlapping/touching intervals
merged = []
cur_start, cur_end = sorted_intervals[0]

for s, e in sorted_intervals[1:]:
    if s <= cur_end:          # overlap or touch: extend
        cur_end = max(cur_end, e)
    else:                     # gap: finalize and start new
        merged.append((cur_start, cur_end))
        cur_start, cur_end = s, e
merged.append((cur_start, cur_end))

# Step 3: Scan merged intervals for answers
longest_milking = max(e - s for s, e in merged)
longest_idle = max(
    (merged[i][0] - merged[i-1][1] for i in range(1, len(merged))),
    default=0
)
```

### Solution

> **Merged intervals**:
>   - `[300, 1200)` -- Farmers 1 and 2 overlap (700 <= 1000), so their shifts merge
>   - `[1500, 2100)` -- Farmer 3 is separate (1500 > 1200)
>
> **Answer**:
>   - Longest continuous milking: **900 seconds** (the `[300, 1200)` block)
>   - Longest idle gap: **300 seconds** (from 1200 to 1500)
>
> **Algorithm**: Sort + Merge + Scan | O(N log N) time, O(N) space
> **Time**: < 0.001s
> **Optimal**: Yes (deterministic, complete)
> **Feasible**: Yes (all constraints verified)

### Independent Verification

The solver includes a brute-force verifier that marks every second on a timeline array and counts runs independently:

> ```
> milking_matches_brute_force    PASS
> idle_matches_brute_force       PASS
> all_intervals_covered          PASS
> merged_non_overlapping         PASS
> ```

The brute-force method marks each second in `[300, 2100)` as milking or idle, then scans for the longest consecutive run of each. Both values agree with the sweep algorithm. This is O(T) where T is the time span, which is acceptable for verification but too slow for large instances as a primary solver.

---

## Phase 3: /uber-interpret

```
/uber-interpret
```

Claude translates the verified solution back into plain language with visualization and sensitivity analysis.

### Bottom Line

> The cows are milked continuously for at most **900 seconds** (15 minutes) at a stretch. The longest period with no milking at all is **300 seconds** (5 minutes), between the end of the morning shift overlap and the start of Farmer 3's shift.

### Timeline Visualization

Claude generates a timeline chart (see `examples/milking-cows/milk2_viz.py`) showing:

- **Top panel**: Individual farmer intervals as horizontal bars, with the overlap between Farmers 1 and 2 annotated
- **Bottom panel**: Merged timeline with the 900-second milking block in green and the 300-second idle gap in red

```
Farmer 1  |████████████████████████|                              (300-1000)
Farmer 2           |████████████████████|                         (700-1200)
Farmer 3                                    |████████████████████| (1500-2100)
          ─────────────────────────────────────────────────────────
Merged    |████████████████████████████████|    |████████████████████|
          300          ←  900s  →        1200   1500  ← 600s →  2100
                                          ← 300s idle →
```

### Sensitivity Analysis

> **What if Farmer 2's shift extends to 1500?**
> The gap disappears entirely. Merged result: one block `[300, 2100)` of 1800 seconds. Longest idle = 0. A single shift extension eliminates all downtime.
>
> **What if a 4th farmer covers the gap (1200-1500)?**
> Same effect -- one continuous block. If minimizing idle time is the goal, adding 300 seconds of coverage at `[1200, 1500)` is the cheapest fix.
>
> **What if Farmer 1 starts later (500 instead of 300)?**
> Merged block becomes `[500, 1200)` = 700 seconds. The longest milking drops from 900 to 700. The solution is moderately sensitive to Farmer 1's start time.

### Modeling Insight

> **Pattern**: "Overlapping time intervals with aggregate queries" maps to **interval merging on a sorted list**.
>
> **Other applications of this pattern**:
> - Meeting room scheduling (merge overlapping meetings to count rooms)
> - Network session analysis (merge overlapping connections to find peak usage)
> - Genomics (merge overlapping gene annotations on a chromosome)
> - Calendar free/busy computation (merge busy blocks to find free windows)
>
> **Key heuristic**: Polya's "Look at the unknown!" -- the unknown is a *property of the union* of intervals, which points directly to merging as the core operation.

---

## Running the Code

```bash
cd examples/milking-cows/

# Run the full solver with verification and test cases
python milk2.py

# Run the USACO-format solver (reads milk2.in, writes milk2.out)
python milk2_usaco.py

# Generate the timeline and algorithm visualizations
python milk2_viz.py
```

Expected output from `milk2.py`:

```
  MILKING COWS (USACO milk2) -- Solution Report

  Input: 3 intervals
    [300, 1000] (duration: 700s)
    [700, 1200] (duration: 500s)
    [1500, 2100] (duration: 600s)

  Merged intervals: 2
    [300, 1200] (duration: 900s)
    [1500, 2100] (duration: 600s)

  ANSWER: 900 300

  INDEPENDENT VERIFICATION (brute-force timeline)
  milking_matches_brute_force     PASS
  idle_matches_brute_force        PASS
  all_intervals_covered           PASS
  merged_non_overlapping          PASS

  All test cases PASSED
```

---

## What You Learned

| Concept | Lesson |
|---------|--------|
| **Modeling** | "Overlapping intervals with aggregate queries" is interval merging |
| **Algorithm** | Sort + linear sweep is O(N log N) and exact -- no approximation needed |
| **Verification** | Brute-force timeline marking is an independent cross-check |
| **Interpretation** | The idle gap is the actionable insight -- it tells you where to add coverage |
| **Sensitivity** | A single 300-second shift extension eliminates all downtime |

Next: [Inspector Assignment Walkthrough](inspector-assignment-walkthrough.md) -- a more complex optimization problem with ILP, LP relaxation, and stakeholder-ready visualizations.

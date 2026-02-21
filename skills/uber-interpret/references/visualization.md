# Visualization Guide

**Scope**: Universal (chart types apply to all domains)

Which chart for which result type. matplotlib/seaborn/NetworkX templates for common mathematical outputs. Audience adaptation rules.

**Libraries**: `matplotlib`, `seaborn`, `networkx` (drawing), `numpy`
**Output**: Always save to PNG at dpi=150 with `bbox_inches='tight'`
**Backend**: Always set `matplotlib.use('Agg')` before importing pyplot

---

## Chart Selection Matrix

| Result Type | Primary Chart | When to Use Secondary | Secondary Chart |
|---|---|---|---|
| Assignment / matching | Assignment matrix heatmap | Many entities | Bipartite graph diagram |
| Shortest path | Annotated graph | Few nodes (≤30) | Bar chart of edge costs |
| Graph coloring | Colored graph diagram | Few nodes (≤50) | Bar chart of color class sizes |
| Network flow | Flow graph with edge labels | Utilization view needed | Sankey diagram |
| Schedule | Gantt chart | Resource utilization view | Stacked bar (utilization) |
| Optimization objective | Bar chart of variable values | Trade-off view | Pareto frontier scatter |
| Sensitivity | Tornado diagram | Multi-parameter view | Spider/radar chart |
| Scenario comparison | Grouped bar chart | Continuous trade-off | Line plot |
| Distribution / counting | Bar chart / histogram | Proportions | Pie chart (≤6 slices) |
| Probability | PMF bar chart | Cumulative view | CDF step plot |
| Tree / hierarchy | Dendrogram or tree layout | Large tree | Treemap |
| Partial order / lattice | Hasse diagram | Few elements (≤20) | Matrix heatmap |
| Partition / clustering | Colored scatter or group diagram | Many clusters | Bar chart of cluster sizes |
| Proof steps | Numbered text or flow diagram | Complex branching | Decision tree diagram |
| Hypothesis test / group comparison | Bar chart with CI error bars | Multiple groups | Box plot / violin plot |
| Distribution comparison | Histogram + KDE overlay | Normality check | QQ plot |
| Regression fit | Scatter + regression line + CI band | Diagnostics needed | Residual plot (fitted vs. residuals) |
| Multiple effect sizes | Forest plot | Single study context | Bar chart with CI |
| Bayesian posterior | Posterior density plot | Prior comparison | Prior vs. posterior overlay |
| Survival curves | Kaplan-Meier step plot | Group comparison | Hazard ratio forest plot |
| Matrix / linear system | Matrix heatmap | Structure view | Spy plot (sparsity) |
| Eigenvalues / singular values | Scree plot / spectrum | Explained variance | Cumulative variance line |
| Function / derivative | Annotated function plot | Multiple functions | Subplot grid |
| Integral / area | Shaded area under curve | Comparison | Side-by-side fill plots |
| Geometry / spatial | Annotated geometric diagram | 3D view | Matplotlib 3D projection |
| Cash flow / investment | Cash flow bar chart | Cumulative view | Running NPV line |
| Amortization | Stacked area (principal vs. interest) | Comparison | Side-by-side schedules |
| Payoff matrix / game | Heatmap with annotations | Strategy comparison | Bar chart of payoffs |
| Sensitivity / tornado | Horizontal bar chart (low/high) | Many parameters | Spider/radar chart |
| Pareto frontier | Scatter plot (objective space) | Knee point highlight | Parallel coordinates |
| Time series decomposition | 4-panel subplot (obs/trend/season/resid) | Single component | Line plot |
| Time series forecast | Line + CI band | Multiple models | Multi-line overlay |
| Survival curves | KM step plot + CI band | Group comparison | Hazard ratio forest plot |
| Change points | Line + vertical markers | Regime coloring | Segment mean overlay |
| Anomalies | Line + highlighted outliers | Context needed | Rolling statistics overlay |
| Confusion matrix | Annotated heatmap | Multi-class | Normalized confusion matrix |
| Classification performance | ROC curve | Precision-recall trade-off | PR curve |
| Cluster assignments | 2D scatter (PCA/UMAP) | Cluster profiles | Radar/bar chart per cluster |
| Feature importance | Horizontal bar chart | Comparison | Grouped bar (multiple models) |
| Explained variance | Scree plot | Cumulative view | Cumulative variance line |

---

## 1. Graph Diagram (Annotated)

**Use for**: Paths, matchings, colorings, flows, connectivity, any graph result with ≤50 nodes.

```python
#!/usr/bin/env python3
"""Annotated graph visualization."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

G = nx.Graph()
# ... build graph

# Layout
pos = nx.spring_layout(G, seed=42)  # deterministic layout
# Alternatives: nx.kamada_kawai_layout, nx.planar_layout, nx.shell_layout

fig, ax = plt.subplots(figsize=(10, 8))

# Draw base graph
nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#cccccc', width=1)
nx.draw_networkx_labels(G, pos, ax=ax, font_size=9)

# Highlight solution (e.g., path, matching)
solution_edges = [('a', 'b'), ('b', 'c')]  # edges in solution
nx.draw_networkx_edges(G, pos, edgelist=solution_edges, ax=ax,
                       edge_color='#d32f2f', width=3)

# Color nodes by role
color_map = {'source': '#4caf50', 'target': '#f44336', 'path': '#ff9800', 'other': '#e0e0e0'}
node_colors = [color_map.get(role[n], '#e0e0e0') for n in G.nodes()]
nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors, node_size=500)

# Edge labels (weights, flow values)
edge_labels = {(u, v): "{:.0f}".format(d['weight']) for u, v, d in G.edges(data=True)}
nx.draw_networkx_edge_labels(G, pos, edge_labels, ax=ax, font_size=8)

ax.set_title('Shortest Path: A → F (total cost: 23)', fontsize=14, fontweight='bold')
ax.axis('off')
plt.tight_layout()
plt.savefig('graph_solution.png', dpi=150, bbox_inches='tight')
```

**Customization by result type**:
- **Shortest path**: Highlight path edges in red, source in green, target in red
- **Matching**: Color matched edges thick, unmatched thin, exposed vertices differently
- **Coloring**: Node color = assigned color, use a colorblind-friendly palette
- **Flow**: Edge width proportional to flow, label with flow/capacity
- **SCC**: Different color per component

---

## 2. Assignment Matrix Heatmap

**Use for**: Bipartite matching, assignment results, qualification matrices.

```python
#!/usr/bin/env python3
"""Assignment matrix heatmap."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Data
rows = ['Emp A', 'Emp B', 'Emp C', 'Emp D']
cols = ['Proj 1', 'Proj 2', 'Proj 3', 'Proj 4', 'Proj 5']
scores = np.array([...])  # qualification/skill scores

# Highlight assignments
assignments = {(0, 2), (1, 0), (2, 4), (3, 1)}  # (row, col) pairs

fig, ax = plt.subplots(figsize=(10, 6))
sns.heatmap(scores, annot=True, fmt='.0f', cmap='YlOrRd',
            xticklabels=cols, yticklabels=rows, ax=ax,
            linewidths=0.5, linecolor='white')

# Mark assignments with bold border
for (r, c) in assignments:
    ax.add_patch(plt.Rectangle((c, r), 1, 1, fill=False,
                                edgecolor='#1a237e', linewidth=3))

ax.set_title('Optimal Assignment (total score: 47)', fontsize=14, fontweight='bold')
ax.set_xlabel('Projects')
ax.set_ylabel('Employees')
plt.tight_layout()
plt.savefig('assignment_matrix.png', dpi=150, bbox_inches='tight')
```

---

## 3. Gantt Chart

**Use for**: Scheduling results, timeline visualization, project plans.

```python
#!/usr/bin/env python3
"""Gantt chart for scheduling results."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Schedule data: (task_name, machine, start, duration, is_critical)
schedule = [
    ('Task A', 0, 0, 3, True),
    ('Task B', 1, 0, 2, False),
    ('Task C', 0, 3, 4, True),
    ('Task D', 1, 2, 3, False),
    ('Task E', 0, 7, 2, True),
]

machines = ['Machine 1', 'Machine 2']
colors_normal = '#64b5f6'
colors_critical = '#e53935'

fig, ax = plt.subplots(figsize=(12, 4))
for task, machine, start, dur, critical in schedule:
    color = colors_critical if critical else colors_normal
    ax.barh(machine, dur, left=start, height=0.6, color=color,
            edgecolor='white', linewidth=1)
    ax.text(start + dur / 2, machine, task, ha='center', va='center',
            fontsize=9, fontweight='bold', color='white')

ax.set_yticks(range(len(machines)))
ax.set_yticklabels(machines)
ax.set_xlabel('Time')
ax.set_title('Optimal Schedule (makespan: 9)', fontsize=14, fontweight='bold')
ax.legend(handles=[
    mpatches.Patch(color=colors_critical, label='Critical path'),
    mpatches.Patch(color=colors_normal, label='Non-critical'),
], loc='upper right')
ax.set_xlim(0, None)
plt.tight_layout()
plt.savefig('gantt_schedule.png', dpi=150, bbox_inches='tight')
```

---

## 4. Tornado Diagram (Sensitivity)

**Use for**: Sensitivity analysis showing impact of each parameter.

```python
#!/usr/bin/env python3
"""Tornado diagram for sensitivity analysis."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Sensitivity data: (parameter_name, low_impact, high_impact)
# Impact = change in objective when parameter is at low/high value
data = [
    ('Employee capacity', -8.5, +10.6),
    ('Min qualification', -17.0, +3.2),
    ('Number of projects', -12.0, +5.0),
    ('Budget limit', -5.0, +15.0),
    ('Deadline', -3.0, +2.0),
]

# Sort by total range (most sensitive first)
data.sort(key=lambda x: abs(x[2] - x[1]), reverse=True)

labels = [d[0] for d in data]
lows = [d[1] for d in data]
highs = [d[2] for d in data]

fig, ax = plt.subplots(figsize=(10, 5))
y_pos = range(len(labels))

ax.barh(y_pos, highs, color='#4caf50', height=0.4, label='Increase parameter')
ax.barh(y_pos, lows, color='#f44336', height=0.4, label='Decrease parameter')
ax.axvline(x=0, color='black', linewidth=0.8)

ax.set_yticks(y_pos)
ax.set_yticklabels(labels)
ax.set_xlabel('Change in Objective (%)')
ax.set_title('Sensitivity Analysis', fontsize=14, fontweight='bold')
ax.legend(loc='lower right')

# Annotate values
for i, (lo, hi) in enumerate(zip(lows, highs)):
    if lo != 0:
        ax.text(lo - 0.5, i, '{:+.1f}%'.format(lo), va='center', ha='right', fontsize=8)
    if hi != 0:
        ax.text(hi + 0.5, i, '{:+.1f}%'.format(hi), va='center', ha='left', fontsize=8)

plt.tight_layout()
plt.savefig('sensitivity_tornado.png', dpi=150, bbox_inches='tight')
```

---

## 5. Scenario Comparison (Grouped Bar)

**Use for**: What-if analysis, comparing 2-5 alternative scenarios.

```python
#!/usr/bin/env python3
"""Scenario comparison bar chart."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

scenarios = ['Current\nOptimal', 'Employee 2\nLeaves', 'Add 9th\nProject', 'Gender\nBalance']
metrics = {
    'Objective Score': [47, 38, 43, 41],
    'Utilization %': [85, 72, 90, 82],
}

x = np.arange(len(scenarios))
width = 0.35
colors = ['#1976d2', '#ff9800']

fig, ax = plt.subplots(figsize=(10, 6))
for i, (metric, values) in enumerate(metrics.items()):
    bars = ax.bar(x + i * width, values, width, label=metric, color=colors[i])
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                str(val), ha='center', va='bottom', fontsize=9)

ax.set_xticks(x + width / 2)
ax.set_xticklabels(scenarios)
ax.set_ylabel('Value')
ax.set_title('What-If Scenario Comparison', fontsize=14, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig('scenario_comparison.png', dpi=150, bbox_inches='tight')
```

---

## 6. Distribution / Counting Bar Chart

**Use for**: Counting results, probability distributions, category breakdowns.

```python
#!/usr/bin/env python3
"""Distribution bar chart."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

categories = ['Type A', 'Type B', 'Type C', 'Type D', 'Type E']
counts = [1250, 980, 670, 340, 160]
total = sum(counts)

fig, ax = plt.subplots(figsize=(10, 5))
bars = ax.bar(categories, counts, color='#42a5f5', edgecolor='white', linewidth=1)

# Annotate with count and percentage
for bar, count in zip(bars, counts):
    pct = count / total * 100
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
            '{:,} ({:.1f}%)'.format(count, pct),
            ha='center', va='bottom', fontsize=9)

ax.set_ylabel('Count')
ax.set_title('Distribution of Solutions by Type (N={:,})'.format(total),
             fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('distribution.png', dpi=150, bbox_inches='tight')
```

---

## 7. Pareto Frontier (Trade-off)

**Use for**: Multi-objective optimization, showing trade-offs between competing objectives.

```python
#!/usr/bin/env python3
"""Pareto frontier scatter plot."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# All feasible solutions: (objective1, objective2)
all_solutions = np.array([(10, 50), (20, 45), (30, 35), (35, 30),
                           (40, 28), (45, 25), (50, 20),
                           (15, 40), (25, 38), (33, 32)])

# Pareto-optimal solutions (manually identified or computed)
pareto = np.array([(10, 50), (20, 45), (30, 35), (40, 28), (50, 20)])

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(all_solutions[:, 0], all_solutions[:, 1],
           c='#bbdefb', s=60, label='Feasible solutions', zorder=2)
ax.scatter(pareto[:, 0], pareto[:, 1],
           c='#d32f2f', s=100, label='Pareto-optimal', zorder=3)
ax.plot(pareto[:, 0], pareto[:, 1], '--', color='#d32f2f', alpha=0.5, zorder=1)

# Annotate key points
ax.annotate('Best for Obj 2', xy=(10, 50), xytext=(15, 52),
            arrowprops=dict(arrowstyle='->', color='gray'), fontsize=9)
ax.annotate('Best for Obj 1', xy=(50, 20), xytext=(45, 15),
            arrowprops=dict(arrowstyle='->', color='gray'), fontsize=9)

ax.set_xlabel('Objective 1 (maximize)')
ax.set_ylabel('Objective 2 (maximize)')
ax.set_title('Pareto Frontier: Trade-off Between Objectives',
             fontsize=14, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.savefig('pareto_frontier.png', dpi=150, bbox_inches='tight')
```

---

## 8. Flow Diagram

**Use for**: Network flow results with capacity utilization.

```python
#!/usr/bin/env python3
"""Network flow visualization."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

G = nx.DiGraph()
# Add edges with capacity and flow
edges = [
    ('S', 'A', 10, 8), ('S', 'B', 7, 7),
    ('A', 'C', 5, 5), ('A', 'D', 6, 3),
    ('B', 'D', 8, 7), ('C', 'T', 9, 5),
    ('D', 'T', 10, 10),
]
for u, v, cap, flow in edges:
    G.add_edge(u, v, capacity=cap, flow=flow)

pos = {'S': (0, 1), 'A': (1, 2), 'B': (1, 0), 'C': (2, 2), 'D': (2, 0), 'T': (3, 1)}

fig, ax = plt.subplots(figsize=(10, 6))

# Draw edges with width proportional to flow
for u, v, d in G.edges(data=True):
    flow, cap = d['flow'], d['capacity']
    utilization = flow / cap if cap > 0 else 0
    color = '#d32f2f' if utilization >= 0.95 else '#ff9800' if utilization >= 0.5 else '#4caf50'
    width = 1 + 4 * utilization
    ax.annotate('', xy=pos[v], xytext=pos[u],
                arrowprops=dict(arrowstyle='->', color=color, lw=width))

# Edge labels: flow/capacity
for u, v, d in G.edges(data=True):
    mid_x = (pos[u][0] + pos[v][0]) / 2
    mid_y = (pos[u][1] + pos[v][1]) / 2 + 0.1
    ax.text(mid_x, mid_y, '{}/{}'.format(d['flow'], d['capacity']),
            ha='center', fontsize=9, fontweight='bold')

# Nodes
for node, (x, y) in pos.items():
    color = '#4caf50' if node == 'S' else '#f44336' if node == 'T' else '#e0e0e0'
    ax.scatter(x, y, s=800, c=color, zorder=5, edgecolors='black', linewidth=1.5)
    ax.text(x, y, node, ha='center', va='center', fontsize=12, fontweight='bold', zorder=6)

ax.set_title('Network Flow (max flow = 15)', fontsize=14, fontweight='bold')
ax.set_xlim(-0.5, 3.5)
ax.set_ylim(-0.5, 2.7)
ax.axis('off')
plt.tight_layout()
plt.savefig('flow_diagram.png', dpi=150, bbox_inches='tight')
```

---

## 9. Hasse Diagram (Partial Order)

**Use for**: Partial orders, lattice structures, dependency hierarchies.

```python
#!/usr/bin/env python3
"""Hasse diagram for partial order."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx

# Build DAG of covering relations (transitive reduction)
H = nx.DiGraph()
H.add_edges_from([
    ('{a}', '{a,b}'), ('{a}', '{a,c}'),
    ('{b}', '{a,b}'), ('{b}', '{b,c}'),
    ('{c}', '{a,c}'), ('{c}', '{b,c}'),
    ('{a,b}', '{a,b,c}'), ('{a,c}', '{a,b,c}'), ('{b,c}', '{a,b,c}'),
    ('{}', '{a}'), ('{}', '{b}'), ('{}', '{c}'),
])

# Layered layout (by level in the Hasse diagram)
levels = {
    '{}': 0,
    '{a}': 1, '{b}': 1, '{c}': 1,
    '{a,b}': 2, '{a,c}': 2, '{b,c}': 2,
    '{a,b,c}': 3,
}
pos = {}
for level in range(4):
    nodes_at_level = [n for n, l in levels.items() if l == level]
    for i, n in enumerate(nodes_at_level):
        x = (i - (len(nodes_at_level) - 1) / 2) * 2
        pos[n] = (x, level * 1.5)

fig, ax = plt.subplots(figsize=(8, 8))
nx.draw(H, pos, ax=ax, with_labels=True, node_color='#e3f2fd',
        node_size=1500, font_size=9, arrows=True,
        edge_color='#90a4ae', arrowsize=15)
ax.set_title('Power Set Lattice P({a, b, c})', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('hasse_diagram.png', dpi=150, bbox_inches='tight')
```

---

## 10. Proof Step Visualization

**Use for**: Presenting proof structure, logical arguments.

For proofs, text-based presentation is usually clearer than graphical. Use a structured format:

```
## Proof Visualization

┌─────────────────────────────────────────────┐
│ CLAIM: For all n ≥ 1, 1³+2³+...+n³ = [n(n+1)/2]²  │
└─────────────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ BASE CASE: n = 1               │
│ LHS = 1³ = 1                   │
│ RHS = [1·2/2]² = 1             │
│ LHS = RHS ✓                    │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ INDUCTIVE HYPOTHESIS            │
│ Assume true for n = k:          │
│ 1³+2³+...+k³ = [k(k+1)/2]²    │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ INDUCTIVE STEP: Show for n=k+1 │
│ LHS = [k(k+1)/2]² + (k+1)³    │
│     = (k+1)²[k²/4 + (k+1)]    │
│     = (k+1)²(k+2)²/4           │
│     = [(k+1)(k+2)/2]²          │
│     = RHS ✓                     │
└─────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────┐
│ ∎ By mathematical induction,    │
│   the claim holds for all n ≥ 1 │
└─────────────────────────────────┘
```

---

## Design Principles

### Color Palette (Colorblind-Friendly)

```python
COLORS = {
    'primary':    '#1976d2',  # Blue
    'secondary':  '#ff9800',  # Orange
    'success':    '#4caf50',  # Green
    'danger':     '#d32f2f',  # Red
    'warning':    '#ffc107',  # Amber
    'info':       '#00bcd4',  # Cyan
    'neutral':    '#9e9e9e',  # Gray
    'background': '#fafafa',  # Light gray
}

# For categorical data (up to 8 categories)
CATEGORICAL = ['#1976d2', '#d32f2f', '#4caf50', '#ff9800',
               '#9c27b0', '#00bcd4', '#795548', '#607d8b']

# For sequential data (light to dark)
SEQUENTIAL = ['#e3f2fd', '#90caf9', '#42a5f5', '#1976d2', '#0d47a1']

# For diverging data (negative to positive)
DIVERGING_NEG = '#d32f2f'
DIVERGING_ZERO = '#fafafa'
DIVERGING_POS = '#4caf50'
```

### Typography

- Title: 14pt, bold
- Axis labels: 11pt, regular
- Tick labels: 9pt
- Annotations: 9pt
- Legend: 9pt

### Layout Rules

1. One message per chart (don't combine unrelated data)
2. Left-to-right for time, bottom-to-top for quantity
3. Start bar charts at zero (don't truncate)
4. No 3D charts (distort perception)
5. No dual y-axes (confusing)
6. Label directly on the chart when possible (avoid forcing legend lookups)
7. Use .format() instead of f-strings in chart code (notebook compatibility)

### Audience Adaptation

**Technical audience**:
- Include axis scales and units
- Show confidence intervals or error bars
- Use log scales when data spans orders of magnitude
- Include statistical annotations (p-values, R², etc.)

**Decision-makers**:
- Larger fonts, fewer data points
- Highlight the key takeaway in the title
- Use traffic-light colors (red/amber/green) for status
- Add a text box with the bottom line

**General audience**:
- Minimize chart jargon
- Add descriptive subtitle explaining what to look at
- Use familiar analogies in annotations
- Round numbers to 2 significant figures

---

## Cross-Reference Index

| Chart Type | Best For (interpretation-patterns.md) | Typical Algorithms (algorithms.md) |
|---|---|---|
| §1 Graph Diagram | §1.1 Shortest Path, §1.3 Coloring, §1.4 Flow, §1.5 Connectivity | §1-§9 Graph algorithms |
| §2 Assignment Heatmap | §1.2 Matching Results | §4 Matching (A15-A18) |
| §3 Gantt Chart | §2.3 Scheduling Results | §10 ILP (A32), §1 Topo Sort (A3) |
| §4 Tornado Diagram | §2.1 LP/ILP sensitivity, §7.1 Convex Opt sensitivity | §10 LP/ILP, §21 Continuous Opt |
| §5 Scenario Comparison | §2.1 LP/ILP what-if, §7.3 Nonlinear Opt | §10 LP/ILP, §21 Continuous Opt |
| §6 Distribution Bar | §4 Counting, §5 Probability, §7.2 Least Squares | §15 Counting, §18 Probability, §21 Least Squares |
| §7 Pareto Frontier | §7.1 Convex Opt trade-offs, multi-objective | §21 Continuous Opt (A87-A88) |
| §8 Flow Diagram | §1.4 Flow Results | §5 Network Flow (A19-A20) |
| §9 Hasse Diagram | (Relations & Orders) | §16 Order Theory (A70-A73) |
| §10 Proof Steps | §3 Proof Results | §17 Proof Techniques (A74-A77) |

| §11 Group Comparison | §8.1 Hypothesis Test Results | S6-S13 (t-tests, ANOVA) |
| §12 QQ Plot | Normality diagnostics | S15 (Shapiro-Wilk) |
| §13 Regression Plot | §8.2 Regression Results | S23-S30 (Regression algorithms) |
| §14 Residual Plot | §8.2 Regression diagnostics | S23-S30 (Regression algorithms) |
| §15 Forest Plot | §8.1 Multiple effect sizes | S45 (Effect sizes), S17 (Multiple testing) |
| §16 Posterior Plot | §8.4 Bayesian Results | S31-S35 (Bayesian methods) |

Also see: **common-mistakes.md** §I1-I6 for visualization and interpretation pitfalls.

---

## 11. Group Comparison (Bar Chart with CI)

**Use for**: Comparing means across 2-6 groups with confidence intervals. Hypothesis test visualization.

```python
#!/usr/bin/env python3
"""Group comparison visualization with confidence intervals."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

groups = ['Control', 'Treatment A', 'Treatment B']
means = [4.2, 5.1, 5.8]
ci_lower = [3.8, 4.6, 5.2]
ci_upper = [4.6, 5.6, 6.4]
errors = [[m - lo for m, lo in zip(means, ci_lower)],
          [hi - m for m, hi in zip(means, ci_upper)]]

fig, ax = plt.subplots(figsize=(8, 5))
colors = ['#90caf9', '#42a5f5', '#1976d2']
bars = ax.bar(groups, means, yerr=errors, capsize=8, color=colors,
              edgecolor='white', linewidth=1.5, error_kw={'linewidth': 2})

# Annotate means
for bar, mean in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.15,
            '{:.1f}'.format(mean), ha='center', fontsize=11, fontweight='bold')

# Significance annotation
ax.annotate('', xy=(0, 6.6), xytext=(2, 6.6),
            arrowprops=dict(arrowstyle='-', color='black', lw=1.5))
ax.text(1, 6.7, 'p = 0.003 *', ha='center', fontsize=9)

ax.set_ylabel('Outcome Measure', fontsize=11)
ax.set_title('Treatment Effect Comparison (Mean + 95% CI)', fontsize=14, fontweight='bold')
ax.set_ylim(0, 7.5)
plt.tight_layout()
plt.savefig('group_comparison.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Error bars = CI (not SD), significance brackets with p-values, y-axis starts at zero, direct value annotation.

---

## 12. QQ Plot (Normality Diagnostic)

**Use for**: Visual assessment of whether data follows a theoretical distribution (typically normal).

```python
#!/usr/bin/env python3
"""QQ plot for normality assessment."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
import numpy as np

data = np.random.default_rng(42).normal(loc=5, scale=2, size=100)

fig, ax = plt.subplots(figsize=(6, 6))
res = stats.probplot(data, dist="norm", plot=ax)

ax.get_lines()[0].set_markerfacecolor('#1976d2')
ax.get_lines()[0].set_markeredgecolor('#0d47a1')
ax.get_lines()[0].set_markersize(5)
ax.get_lines()[1].set_color('#d32f2f')

# Add Shapiro-Wilk result
w, p = stats.shapiro(data)
ax.text(0.05, 0.95, 'Shapiro-Wilk: W={:.3f}, p={:.3f}'.format(w, p),
        transform=ax.transAxes, fontsize=9, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax.set_title('QQ Plot: Normality Check', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.savefig('qq_plot.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Points close to diagonal = normal. Curvature at tails indicates skew or heavy tails. Include Shapiro-Wilk test result.

---

## 13. Regression Plot (Scatter + Fit + CI Band)

**Use for**: Visualizing regression fit with confidence band around the predicted line.

```python
#!/usr/bin/env python3
"""Regression plot with confidence band."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

np.random.seed(42)
x = np.linspace(0, 10, 50)
y = 2.5 * x + 3 + np.random.normal(0, 3, 50)

slope, intercept, r, p, se = stats.linregress(x, y)
y_pred = slope * x + intercept

# Confidence band
n = len(x)
x_mean = np.mean(x)
se_fit = np.sqrt(np.sum((y - y_pred)**2) / (n-2) * (1/n + (x - x_mean)**2 / np.sum((x - x_mean)**2)))
t_crit = stats.t.ppf(0.975, df=n-2)

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(x, y, alpha=0.6, color='#1976d2', s=40, label='Observations')
ax.plot(x, y_pred, color='#d32f2f', linewidth=2, label='OLS fit')
ax.fill_between(x, y_pred - t_crit*se_fit, y_pred + t_crit*se_fit,
                alpha=0.2, color='#d32f2f', label='95% CI')

# Annotate
eq = 'y = {:.2f}x + {:.2f}'.format(slope, intercept)
ax.text(0.05, 0.95, '{}\nR² = {:.3f}, p = {:.2e}'.format(eq, r**2, p),
        transform=ax.transAxes, fontsize=10, verticalalignment='top',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax.set_xlabel('Predictor (X)', fontsize=11)
ax.set_ylabel('Response (Y)', fontsize=11)
ax.set_title('Linear Regression with 95% Confidence Band', fontsize=14, fontweight='bold')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('regression_plot.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Scatter + fit line + CI band, equation and R² annotation, labeled axes with units.

---

## 14. Residual Plot (Diagnostics)

**Use for**: Checking regression assumptions (linearity, homoscedasticity, outliers).

```python
#!/usr/bin/env python3
"""Residual diagnostics plot."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# fitted and residuals from regression
fitted = np.array([...])  # predicted values
residuals = np.array([...])  # y - y_pred

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# Residuals vs Fitted
axes[0].scatter(fitted, residuals, alpha=0.6, color='#1976d2', s=30)
axes[0].axhline(y=0, color='#d32f2f', linestyle='--', linewidth=1.5)
axes[0].set_xlabel('Fitted Values', fontsize=11)
axes[0].set_ylabel('Residuals', fontsize=11)
axes[0].set_title('Residuals vs Fitted', fontsize=12, fontweight='bold')

# Histogram of residuals
axes[1].hist(residuals, bins=20, color='#42a5f5', edgecolor='white', density=True)
from scipy.stats import norm
x_range = np.linspace(residuals.min(), residuals.max(), 100)
axes[1].plot(x_range, norm.pdf(x_range, np.mean(residuals), np.std(residuals)),
             color='#d32f2f', linewidth=2, label='Normal fit')
axes[1].set_xlabel('Residual Value', fontsize=11)
axes[1].set_ylabel('Density', fontsize=11)
axes[1].set_title('Residual Distribution', fontsize=12, fontweight='bold')
axes[1].legend(fontsize=9)

plt.suptitle('Regression Diagnostics', fontsize=14, fontweight='bold', y=1.02)
plt.tight_layout()
plt.savefig('residual_plot.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Residuals vs. fitted (check for patterns = nonlinearity, funnel = heteroscedasticity). Residual histogram (check for normality). Outliers > 3 SD.

---

## 15. Forest Plot (Multiple Effect Sizes)

**Use for**: Comparing effect sizes across multiple studies, subgroups, or comparisons.

```python
#!/usr/bin/env python3
"""Forest plot for multiple effect sizes."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

labels = ['Study A', 'Study B', 'Study C', 'Study D', 'Overall']
effects = [0.35, 0.52, 0.28, 0.61, 0.44]
ci_lower = [0.10, 0.30, -0.05, 0.38, 0.32]
ci_upper = [0.60, 0.74, 0.61, 0.84, 0.56]
weights = [20, 30, 15, 25, 100]  # relative weight (%)

fig, ax = plt.subplots(figsize=(8, 5))
y_pos = np.arange(len(labels))

for i, (label, eff, lo, hi, w) in enumerate(zip(labels, effects, ci_lower, ci_upper, weights)):
    color = '#d32f2f' if label == 'Overall' else '#1976d2'
    marker = 'D' if label == 'Overall' else 'o'
    size = w * 3
    ax.errorbar(eff, i, xerr=[[eff-lo], [hi-eff]], fmt=marker, color=color,
                markersize=np.sqrt(size), capsize=4, linewidth=2, capthick=1.5)
    ax.text(hi + 0.05, i, '{:.2f} [{:.2f}, {:.2f}]'.format(eff, lo, hi),
            va='center', fontsize=9)

ax.axvline(x=0, color='gray', linestyle='--', linewidth=1)
ax.set_yticks(y_pos)
ax.set_yticklabels(labels, fontsize=10)
ax.set_xlabel("Effect Size (Cohen's d)", fontsize=11)
ax.set_title('Forest Plot: Effect Size Comparison', fontsize=14, fontweight='bold')
ax.invert_yaxis()
plt.tight_layout()
plt.savefig('forest_plot.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Point estimates with CI bars, vertical line at null (0), diamond for overall/pooled estimate, marker size proportional to weight/sample size.

---

## 16. Posterior Distribution Plot (Bayesian)

**Use for**: Visualizing Bayesian posterior distributions with credible intervals and prior comparison.

```python
#!/usr/bin/env python3
"""Bayesian posterior distribution visualization."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

x = np.linspace(-2, 8, 500)
prior = stats.norm.pdf(x, loc=3, scale=2)
posterior = stats.norm.pdf(x, loc=4.2, scale=0.8)

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, prior, '--', color='#90caf9', linewidth=2, label='Prior')
ax.plot(x, posterior, '-', color='#1976d2', linewidth=2.5, label='Posterior')
ax.fill_between(x, posterior, where=(x >= 2.63) & (x <= 5.77),
                alpha=0.3, color='#1976d2', label='95% HDI')

# Mark MAP estimate
map_val = x[np.argmax(posterior)]
ax.axvline(x=map_val, color='#d32f2f', linestyle=':', linewidth=1.5, label='MAP = {:.1f}'.format(map_val))

# Annotate HDI
ax.annotate('95% HDI: [2.63, 5.77]', xy=(4.2, 0.05), fontsize=9,
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

ax.set_xlabel('Parameter Value', fontsize=11)
ax.set_ylabel('Density', fontsize=11)
ax.set_title('Posterior Distribution (Prior vs. Posterior)', fontsize=14, fontweight='bold')
ax.legend(fontsize=9)
plt.tight_layout()
plt.savefig('posterior_plot.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Prior (dashed) vs. posterior (solid) overlay, shaded HDI region, MAP/mean point estimate, clear axis labels.

---

## 17. Matrix Heatmap

**When to use**: Visualize a matrix (coefficients, correlation, assignment, distance). Reveals structure, sparsity, and magnitude patterns at a glance.

**Template**:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

A = np.array([[4, -2, 1], [-2, 5, -3], [1, -3, 6]])
labels = ['x₁', 'x₂', 'x₃']

fig, ax = plt.subplots(figsize=(6, 5))
sns.heatmap(A, annot=True, fmt='.1f', cmap='RdBu_r', center=0,
            xticklabels=labels, yticklabels=labels, ax=ax)
ax.set_title('Coefficient Matrix A', fontsize=14)
plt.tight_layout()
plt.savefig('matrix_heatmap.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Annotated cell values, diverging colormap centered at 0, labeled axes.

---

## 18. Scree / Spectrum Plot

**When to use**: Show eigenvalues or singular values in descending order. Reveals effective dimensionality and importance of each component.

**Template**:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

singular_values = np.array([10.5, 4.2, 1.8, 0.3, 0.05])
explained = singular_values**2 / np.sum(singular_values**2) * 100
cumulative = np.cumsum(explained)

fig, ax1 = plt.subplots(figsize=(7, 5))
ax1.bar(range(1, len(singular_values)+1), explained, color='#58a6ff', alpha=0.8, label='Individual')
ax2 = ax1.twinx()
ax2.plot(range(1, len(singular_values)+1), cumulative, 'o-', color='#3fb950', label='Cumulative')
ax1.set_xlabel('Component')
ax1.set_ylabel('Explained Variance (%)')
ax2.set_ylabel('Cumulative (%)')
ax2.axhline(y=95, color='gray', linestyle='--', alpha=0.5, label='95% threshold')
ax1.set_title('Singular Value Spectrum')
fig.legend(loc='upper left', bbox_to_anchor=(0.12, 0.88))
plt.tight_layout()
plt.savefig('scree_plot.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Bar chart of individual values, overlaid cumulative line, 95% threshold line, labeled components.

---

## 19. Function Plot (Annotated)

**When to use**: Plot a function with critical points, tangent lines, shaded integrals, or derivative overlays annotated.

**Template**:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-2, 4, 500)
f = x**3 - 3*x**2 + 1
f_prime = 3*x**2 - 6*x

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(x, f, 'b-', linewidth=2, label='f(x) = x³ − 3x² + 1')
ax.plot(x, f_prime, 'r--', linewidth=1.5, label="f'(x) = 3x² − 6x")
# Mark critical points
ax.plot(0, 1, 'go', markersize=10, label='Local max (0, 1)')
ax.plot(2, -3, 'rs', markersize=10, label='Local min (2, −3)')
# Shade integral
mask = (x >= 0) & (x <= 2)
ax.fill_between(x[mask], f[mask], alpha=0.2, color='blue', label='∫₀² f(x)dx')
ax.axhline(0, color='gray', linewidth=0.5)
ax.legend(fontsize=9)
ax.set_title('Function Analysis', fontsize=14)
ax.set_xlabel('x')
ax.set_ylabel('y')
plt.tight_layout()
plt.savefig('function_plot.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Function curve, derivative overlay, annotated critical points (markers + labels), shaded integral region, axis lines.

---

## 20. Geometric Diagram

**When to use**: Visualize polygons, triangles, points, convex hulls, Voronoi diagrams, or other spatial geometry.

**Template**:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Polygon as MplPolygon
from scipy.spatial import ConvexHull

points = np.random.rand(20, 2) * 10
hull = ConvexHull(points)

fig, ax = plt.subplots(figsize=(7, 7))
ax.scatter(points[:, 0], points[:, 1], c='#58a6ff', s=50, zorder=3)
for i, (x, y) in enumerate(points):
    ax.annotate(f'P{i}', (x, y), textcoords='offset points',
                xytext=(5, 5), fontsize=8)
hull_pts = points[hull.vertices]
poly = MplPolygon(hull_pts, fill=True, alpha=0.15, color='#3fb950',
                  edgecolor='#3fb950', linewidth=2)
ax.add_patch(poly)
ax.set_title(f'Convex Hull (area = {hull.volume:.2f})', fontsize=14)
ax.set_aspect('equal')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('geometric_diagram.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Labeled points, polygon fill with transparency, dimensions/measurements annotated, equal aspect ratio, grid.

---

## 21. Cash Flow / Amortization Chart

**When to use**: Visualize investment cash flows (bar chart), NPV accumulation (line), or loan amortization (stacked area of principal vs. interest).

**Template**:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import numpy_financial as npf

rate, nper, pv = 0.05/12, 360, -300000
periods = np.arange(1, nper + 1)
principal = -npf.ppmt(rate, periods, nper, pv)
interest = -npf.ipmt(rate, periods, nper, pv)

fig, ax = plt.subplots(figsize=(10, 5))
ax.stackplot(periods/12, principal, interest,
             labels=['Principal', 'Interest'],
             colors=['#3fb950', '#58a6ff'], alpha=0.8)
ax.set_xlabel('Year')
ax.set_ylabel('Monthly Payment Breakdown ($)')
ax.set_title('Mortgage Amortization: $300K at 5% over 30 Years')
ax.legend(loc='upper right')
ax.set_xlim(0, 30)
plt.tight_layout()
plt.savefig('amortization_chart.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Stacked area (principal grows, interest shrinks over time), clear year axis, dollar labels, total payment line optional.

---

## 22. Payoff Matrix / Game Theory Heatmap

**When to use**: Visualize payoff matrices for 2-player games, Nash equilibrium highlighting, strategy comparison.

**Template**:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

A = np.array([[3, 0], [5, 1]])  # row player payoffs
B = np.array([[3, 5], [0, 1]])  # column player payoffs
row_labels = ['Cooperate', 'Defect']
col_labels = ['Cooperate', 'Defect']

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
for ax, matrix, title in [(axes[0], A, 'Row Player Payoffs'),
                           (axes[1], B, 'Column Player Payoffs')]:
    sns.heatmap(matrix, annot=True, fmt='.1f', cmap='RdYlGn', center=0,
                xticklabels=col_labels, yticklabels=row_labels, ax=ax,
                linewidths=1, linecolor='white', cbar_kws={'shrink': 0.8})
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_xlabel('Column Player')
    ax.set_ylabel('Row Player')
    # Highlight Nash equilibrium cell
    eq_row, eq_col = 1, 1  # example: (Defect, Defect)
    ax.add_patch(plt.Rectangle((eq_col, eq_row), 1, 1,
                               fill=False, edgecolor='red', linewidth=3))
plt.suptitle('Game Payoff Matrix (Nash Equilibrium in red)', fontsize=14)
plt.tight_layout()
plt.savefig('payoff_matrix.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Side-by-side heatmaps for each player, annotated cell values, Nash equilibrium highlighted with red border, diverging colormap centered at 0.

---

## 23. Tornado / Sensitivity Chart

**When to use**: Show which parameters have the most impact on a decision outcome; horizontal bars extending from base case.

**Template**:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

params = ['Market size', 'Price', 'Cost', 'Discount rate', 'Growth rate']
low_impact = [-30000, -20000, -15000, -8000, -5000]
high_impact = [35000, 25000, 12000, 10000, 7000]
base_value = 100000

fig, ax = plt.subplots(figsize=(10, 5))
y_pos = np.arange(len(params))
ax.barh(y_pos, high_impact, align='center', color='#3fb950', alpha=0.8, label='High')
ax.barh(y_pos, low_impact, align='center', color='#f85149', alpha=0.8, label='Low')
ax.set_yticks(y_pos)
ax.set_yticklabels(params)
ax.set_xlabel(f'Change from Base Case (${base_value:,})')
ax.set_title('Sensitivity Analysis — Tornado Diagram', fontsize=14)
ax.axvline(x=0, color='black', linewidth=0.8)
ax.legend(loc='lower right')
for i, (lo, hi) in enumerate(zip(low_impact, high_impact)):
    ax.text(lo - 1000, i, f'${base_value+lo:,}', ha='right', va='center', fontsize=8)
    ax.text(hi + 1000, i, f'${base_value+hi:,}', ha='left', va='center', fontsize=8)
plt.tight_layout()
plt.savefig('tornado_chart.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Horizontal bars sorted by total impact (widest at top), base case line at x=0, red/green for negative/positive impact, value labels at bar ends.

---

## 24. Pareto Frontier Plot

**When to use**: Visualize trade-offs between competing objectives; highlight non-dominated solutions and knee points.

**Template**:
```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

# Objectives for all evaluated solutions
all_f1 = np.random.uniform(0, 10, 50)
all_f2 = 10 - all_f1 + np.random.normal(0, 1.5, 50)
# Pareto front (sorted)
pareto_f1 = np.sort(np.random.uniform(0, 10, 12))
pareto_f2 = 10 - pareto_f1 + np.random.normal(0, 0.3, 12)

fig, ax = plt.subplots(figsize=(8, 6))
ax.scatter(all_f1, all_f2, c='#8b949e', alpha=0.4, s=30, label='Dominated')
ax.scatter(pareto_f1, pareto_f2, c='#58a6ff', s=60, zorder=3, label='Pareto front')
ax.plot(pareto_f1, pareto_f2, c='#58a6ff', linewidth=1.5, alpha=0.7)
# Highlight knee point
knee_idx = len(pareto_f1) // 2
ax.scatter([pareto_f1[knee_idx]], [pareto_f2[knee_idx]],
           c='#f0883e', s=120, zorder=4, marker='*', label='Knee point')
ax.annotate('Knee', (pareto_f1[knee_idx], pareto_f2[knee_idx]),
            textcoords='offset points', xytext=(10, 10), fontsize=10,
            arrowprops=dict(arrowstyle='->', color='#f0883e'))
# Utopia point
ax.scatter([pareto_f1.min()], [pareto_f2.min()], c='#3fb950', s=80,
           marker='D', zorder=4, label='Utopia (infeasible)')
ax.set_xlabel('Objective 1 (Cost)', fontsize=12)
ax.set_ylabel('Objective 2 (Time)', fontsize=12)
ax.set_title('Pareto Frontier — Cost vs. Time Trade-off', fontsize=14)
ax.legend(loc='upper right')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('pareto_frontier.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Dominated points (grey), Pareto front (blue connected), knee point (star), utopia point (diamond), axis labels matching objectives, grid.

---

## 25. Time Series Decomposition Plot

**When to use**: Showing trend, seasonal, and residual components of a time series after STL or classical decomposition.

### Chart Selection Matrix Entry

| Result type | Chart |
|---|---|
| Decomposition (trend + seasonal + residual) | Time Series Decomposition (stacked subplots) |

### Template

```python
import matplotlib.pyplot as plt
import numpy as np

# --- Data: decomposition result ---
# time, observed, trend, seasonal, residual = ...

fig, axes = plt.subplots(4, 1, figsize=(12, 10), sharex=True)

axes[0].plot(time, observed, color='#58a6ff', linewidth=1)
axes[0].set_ylabel('Observed', fontsize=11)
axes[0].set_title('Time Series Decomposition (STL)', fontsize=14)

axes[1].plot(time, trend, color='#f0883e', linewidth=2)
axes[1].set_ylabel('Trend', fontsize=11)

axes[2].plot(time, seasonal, color='#3fb950', linewidth=1)
axes[2].set_ylabel('Seasonal', fontsize=11)
axes[2].axhline(0, color='#8b949e', linewidth=0.5, linestyle='--')

axes[3].scatter(time, residual, color='#8b949e', s=8, alpha=0.5)
axes[3].axhline(0, color='#da3633', linewidth=0.5, linestyle='--')
axes[3].set_ylabel('Residual', fontsize=11)
axes[3].set_xlabel('Time', fontsize=12)

for ax in axes:
    ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('decomposition.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Four vertically-stacked subplots sharing x-axis (time). Observed (blue), trend (orange), seasonal (green, centered on zero), residual (grey scatter, centered on zero). Shared time axis.

---

## 26. Forecast Plot (with Confidence Bands)

**When to use**: Showing historical data, fitted values, and forecasts with uncertainty intervals.

### Chart Selection Matrix Entry

| Result type | Chart |
|---|---|
| Time series forecast (ARIMA, ETS, Prophet) | Forecast Plot with CI bands |

### Template

```python
import matplotlib.pyplot as plt
import numpy as np

# --- Data ---
# hist_time, hist_values = historical time series
# fcast_time, fcast_mean, fcast_lower, fcast_upper = forecast with CI

fig, ax = plt.subplots(figsize=(12, 6))

# Historical data
ax.plot(hist_time, hist_values, color='#58a6ff', linewidth=1.5, label='Observed')

# Forecast
ax.plot(fcast_time, fcast_mean, color='#f0883e', linewidth=2, label='Forecast')
ax.fill_between(fcast_time, fcast_lower, fcast_upper,
                color='#f0883e', alpha=0.2, label='95% CI')

# Vertical line at forecast origin
ax.axvline(x=hist_time[-1], color='#8b949e', linestyle='--', linewidth=1, alpha=0.7)
ax.annotate('Forecast →', xy=(hist_time[-1], max(hist_values)),
            xytext=(10, 5), textcoords='offset points', fontsize=10, color='#8b949e')

ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Value', fontsize=12)
ax.set_title('Sales Forecast — SARIMA(1,1,1)(1,1,1,12)', fontsize=14)
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('forecast.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Historical data (blue solid), forecast (orange solid), confidence interval (orange shaded), vertical dashed line at forecast origin, axis labels, model name in title.

---

## 27. Survival Curve (Kaplan-Meier)

**When to use**: Showing estimated survival probabilities over time, optionally comparing groups.

### Chart Selection Matrix Entry

| Result type | Chart |
|---|---|
| Survival analysis (Kaplan-Meier, Cox PH) | Survival Curve (step function with CI) |

### Template

```python
import matplotlib.pyplot as plt
import numpy as np

# --- Data ---
# timeline_a, survival_a, ci_lower_a, ci_upper_a = Group A KM estimate
# timeline_b, survival_b, ci_lower_b, ci_upper_b = Group B KM estimate
# p_value = log-rank test result

fig, ax = plt.subplots(figsize=(10, 7))

# Group A
ax.step(timeline_a, survival_a, where='post', color='#58a6ff', linewidth=2, label='Group A')
ax.fill_between(timeline_a, ci_lower_a, ci_upper_a, step='post',
                color='#58a6ff', alpha=0.15)

# Group B
ax.step(timeline_b, survival_b, where='post', color='#f0883e', linewidth=2, label='Group B')
ax.fill_between(timeline_b, ci_lower_b, ci_upper_b, step='post',
                color='#f0883e', alpha=0.15)

# Median survival reference lines
ax.axhline(0.5, color='#8b949e', linestyle=':', linewidth=1, alpha=0.5)
ax.annotate('Median survival', xy=(0, 0.5), xytext=(5, 5),
            textcoords='offset points', fontsize=9, color='#8b949e')

# Log-rank test annotation
ax.text(0.95, 0.95, f'Log-rank p = {p_value:.4f}',
        transform=ax.transAxes, ha='right', va='top', fontsize=11,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#8b949e'))

ax.set_xlabel('Time (months)', fontsize=12)
ax.set_ylabel('Survival Probability', fontsize=12)
ax.set_title('Kaplan-Meier Survival Curves', fontsize=14)
ax.set_ylim(0, 1.05)
ax.legend(loc='lower left', fontsize=11)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('survival_curve.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Step function (survival is piecewise constant), confidence bands (shaded), median survival reference line at 0.5, log-rank p-value annotation, y-axis from 0 to 1, group colors for comparison.

---

## 28. Confusion Matrix Heatmap

**When to use**: Classification results — show true vs. predicted labels, identify which classes are confused.

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

# --- Data ---
# confusion_matrix: 2D array (shape [n_classes, n_classes])
# class_names: list of class label strings

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Raw counts
sns.heatmap(confusion_matrix, annot=True, fmt='d', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names, ax=axes[0])
axes[0].set_xlabel('Predicted', fontsize=12)
axes[0].set_ylabel('Actual', fontsize=12)
axes[0].set_title('Confusion Matrix (counts)', fontsize=14)

# Normalized (row-wise = recall per class)
cm_norm = confusion_matrix.astype(float) / confusion_matrix.sum(axis=1, keepdims=True)
sns.heatmap(cm_norm, annot=True, fmt='.2f', cmap='Blues',
            xticklabels=class_names, yticklabels=class_names, ax=axes[1])
axes[1].set_xlabel('Predicted', fontsize=12)
axes[1].set_ylabel('Actual', fontsize=12)
axes[1].set_title('Confusion Matrix (normalized)', fontsize=14)

plt.tight_layout()
plt.savefig('confusion_matrix.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Two panels (raw counts + normalized), Blues colormap, annotated cells, class labels on both axes, row-normalized shows recall per class.

---

## 29. ROC / Precision-Recall Curve

**When to use**: Binary or multi-class classification — show the trade-off between true positive rate and false positive rate (ROC) or precision and recall (PR).

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc, precision_recall_curve, average_precision_score

# --- Data ---
# y_true: true binary labels
# y_prob: predicted probabilities for the positive class
# model_name: string

fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# ROC Curve
fpr, tpr, _ = roc_curve(y_true, y_prob)
roc_auc = auc(fpr, tpr)
axes[0].plot(fpr, tpr, color='#58a6ff', linewidth=2, label=f'{model_name} (AUC = {roc_auc:.3f})')
axes[0].plot([0, 1], [0, 1], color='#8b949e', linestyle='--', linewidth=1, label='Random')
axes[0].fill_between(fpr, tpr, alpha=0.1, color='#58a6ff')
axes[0].set_xlabel('False Positive Rate', fontsize=12)
axes[0].set_ylabel('True Positive Rate', fontsize=12)
axes[0].set_title('ROC Curve', fontsize=14)
axes[0].legend(loc='lower right', fontsize=11)
axes[0].grid(True, alpha=0.3)

# Precision-Recall Curve
precision, recall, _ = precision_recall_curve(y_true, y_prob)
ap = average_precision_score(y_true, y_prob)
axes[1].plot(recall, precision, color='#f0883e', linewidth=2, label=f'{model_name} (AP = {ap:.3f})')
axes[1].fill_between(recall, precision, alpha=0.1, color='#f0883e')
axes[1].set_xlabel('Recall', fontsize=12)
axes[1].set_ylabel('Precision', fontsize=12)
axes[1].set_title('Precision-Recall Curve', fontsize=14)
axes[1].legend(loc='upper right', fontsize=11)
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('roc_pr_curves.png', dpi=150, bbox_inches='tight')
```

**Key elements**: Two panels (ROC + PR), diagonal reference line for ROC (random classifier), AUC/AP annotations in legend, shaded area under curve, grid for readability.

---

## 30. Cluster Scatter Plot (2D Projection)

**When to use**: Clustering results — show cluster assignments in a 2D projection (PCA or UMAP), with centroids and optional decision boundaries.

```python
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from sklearn.decomposition import PCA

# --- Data ---
# X: feature matrix (n_samples, n_features)
# labels: cluster assignments (n_samples,)
# centroids: cluster centers in original space (optional)
# method_name: string (e.g., "K-Means")

# Project to 2D for visualization
pca = PCA(n_components=2)
X_2d = pca.fit_transform(X)

colors = ['#58a6ff', '#f0883e', '#3fb950', '#bc8cff', '#f778ba', '#d29922']
fig, ax = plt.subplots(figsize=(10, 7))

unique_labels = sorted(set(labels))
for i, label in enumerate(unique_labels):
    if label == -1:  # Noise (DBSCAN)
        mask = labels == label
        ax.scatter(X_2d[mask, 0], X_2d[mask, 1], c='#8b949e', marker='x',
                   s=30, alpha=0.5, label='Noise')
    else:
        mask = labels == label
        ax.scatter(X_2d[mask, 0], X_2d[mask, 1], c=colors[i % len(colors)],
                   s=50, alpha=0.6, label=f'Cluster {label} (n={mask.sum()})')

# Plot centroids if available
if centroids is not None:
    centroids_2d = pca.transform(centroids)
    ax.scatter(centroids_2d[:, 0], centroids_2d[:, 1], c='red', marker='*',
               s=200, edgecolors='black', linewidths=1, zorder=5, label='Centroids')

ax.set_xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%} variance)', fontsize=12)
ax.set_ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%} variance)', fontsize=12)
ax.set_title(f'{method_name} Clustering (2D PCA Projection)', fontsize=14)
ax.legend(loc='best', fontsize=10)
ax.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig('cluster_scatter.png', dpi=150, bbox_inches='tight')
```

**Key elements**: PCA 2D projection with explained variance on axes, distinct colors per cluster, noise points as gray X markers (DBSCAN), centroids as red stars, cluster sizes in legend, grid for readability.

# Visualization Guide

Which chart for which result type. matplotlib/seaborn/NetworkX templates for every common discrete math output. Audience adaptation rules.

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

#!/usr/bin/env python3
"""Visualizations for Food Safety Inspector Assignment interpretation."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# --- Colorblind-friendly palette ---
COLORS = {
    'primary':   '#1976d2',
    'secondary': '#ff9800',
    'success':   '#4caf50',
    'danger':    '#d32f2f',
    'warning':   '#ffc107',
    'info':      '#00bcd4',
    'neutral':   '#9e9e9e',
}
CATEGORICAL = ['#1976d2', '#d32f2f', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4']

# === DATA ===
inspectors = ['Alice', 'Bob', 'Carol', 'Dave', 'Eve', 'Frank']
facilities = ['F1\ndairy', 'F2\ndairy', 'F3\nmeat', 'F4\nmeat', 'F5\nbakery',
              'F6\nbakery', 'F7\nseafood', 'F8\nseafood', 'F9\nbev', 'F10\nbev']
facility_labels = ['F1', 'F2', 'F3', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10']

score_matrix = np.array([
    [9, 9, 7, 7, 4, 4, 3, 3, 6, 6],   # Alice
    [5, 5, 9, 9, 6, 6, 8, 8, 3, 3],   # Bob
    [7, 7, 4, 4, 9, 9, 5, 5, 8, 8],   # Carol
    [3, 3, 6, 6, 5, 5, 9, 9, 4, 4],   # Dave
    [6, 6, 3, 3, 7, 7, 4, 4, 9, 9],   # Eve
    [8, 8, 5, 5, 3, 3, 6, 6, 7, 7],   # Frank
])

# Optimal assignments: (inspector_idx, facility_idx)
assignments = [(0,0), (0,1), (1,2), (1,3), (2,4), (2,5), (3,6), (3,7), (4,8), (4,9)]

# Sensitivity data
sensitivity = {
    'Alice': {'obj': 88, 'delta': -2, 'pct': -2.2},
    'Bob':   {'obj': 85, 'delta': -5, 'pct': -5.6},
    'Carol': {'obj': 85, 'delta': -5, 'pct': -5.6},
    'Dave':  {'obj': 86, 'delta': -4, 'pct': -4.4},
    'Eve':   {'obj': 87, 'delta': -3, 'pct': -3.3},
    'Frank': {'obj': 90, 'delta':  0, 'pct':  0.0},
}


# =========================================
# CHART 1: Assignment Matrix Heatmap
# =========================================
fig, ax = plt.subplots(figsize=(12, 5.5))

# Create heatmap manually for control
im = ax.imshow(score_matrix, cmap='YlOrRd', aspect='auto', vmin=1, vmax=10)

# Annotate each cell
for i in range(6):
    for j in range(10):
        val = score_matrix[i, j]
        color = 'white' if val >= 7 else 'black'
        fontweight = 'bold' if (i, j) in assignments else 'normal'
        ax.text(j, i, str(val), ha='center', va='center',
                fontsize=11, color=color, fontweight=fontweight)

# Mark optimal assignments with thick border
for (r, c) in assignments:
    ax.add_patch(plt.Rectangle((c - 0.5, r - 0.5), 1, 1, fill=False,
                                edgecolor='#1a237e', linewidth=3.5))

ax.set_xticks(range(10))
ax.set_xticklabels(['F1\n(dairy)', 'F2\n(dairy)', 'F3\n(meat)', 'F4\n(meat)',
                     'F5\n(bakery)', 'F6\n(bakery)', 'F7\n(seafood)', 'F8\n(seafood)',
                     'F9\n(bev)', 'F10\n(bev)'], fontsize=9)
ax.set_yticks(range(6))
ax.set_yticklabels(inspectors, fontsize=11)
ax.set_xlabel('Facilities (type)', fontsize=11)
ax.set_ylabel('Inspectors', fontsize=11)
ax.set_title('Optimal Inspector Assignment (Score = 90/90 = 100%)\nBlue borders = assigned pairs | Values = expertise scores (1-10)',
             fontsize=13, fontweight='bold')

cbar = plt.colorbar(im, ax=ax, shrink=0.8)
cbar.set_label('Expertise Score', fontsize=10)

plt.tight_layout()
plt.savefig('viz_assignment_matrix.png', dpi=150, bbox_inches='tight')
print("Saved: viz_assignment_matrix.png")
plt.close()


# =========================================
# CHART 2: Sensitivity Tornado Diagram
# =========================================
fig, ax = plt.subplots(figsize=(10, 5))

# Sort by impact magnitude (most impactful first)
sorted_inspectors = sorted(sensitivity.keys(), key=lambda x: abs(sensitivity[x]['delta']))
y_pos = range(len(sorted_inspectors))
deltas = [sensitivity[i]['delta'] for i in sorted_inspectors]
pcts = [sensitivity[i]['pct'] for i in sorted_inspectors]

bar_colors = [COLORS['danger'] if d < -4 else COLORS['warning'] if d < 0 else COLORS['success']
              for d in deltas]

bars = ax.barh(y_pos, deltas, color=bar_colors, height=0.6, edgecolor='white', linewidth=1)
ax.axvline(x=0, color='black', linewidth=1)

ax.set_yticks(y_pos)
ax.set_yticklabels(['{} leaves'.format(i) for i in sorted_inspectors], fontsize=11)
ax.set_xlabel('Change in Total Expertise Score', fontsize=11)
ax.set_title('Personnel Risk: Impact of Losing Each Inspector\n(Current optimal = 90 points)',
             fontsize=13, fontweight='bold')

# Annotate
for i, (d, p) in enumerate(zip(deltas, pcts)):
    label = '{:+d} ({:+.1f}%)'.format(d, p) if d != 0 else 'No impact'
    x_offset = -0.3 if d < 0 else 0.3
    ha = 'right' if d < 0 else 'left'
    ax.text(d + x_offset, i, label, va='center', ha=ha, fontsize=10, fontweight='bold')

# Risk legend
legend_elements = [
    mpatches.Patch(color=COLORS['danger'], label='MODERATE risk (>5% drop)'),
    mpatches.Patch(color=COLORS['warning'], label='LOW risk (1-5% drop)'),
    mpatches.Patch(color=COLORS['success'], label='No impact'),
]
ax.legend(handles=legend_elements, loc='lower left', fontsize=9)

ax.set_xlim(-7, 2)
plt.tight_layout()
plt.savefig('viz_sensitivity_tornado.png', dpi=150, bbox_inches='tight')
print("Saved: viz_sensitivity_tornado.png")
plt.close()


# =========================================
# CHART 3: Inspector Workload & Expertise
# =========================================
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

# Left: Workload (facilities per inspector)
loads = [2, 2, 2, 2, 2, 0]
scores = [18, 18, 18, 18, 18, 0]
specialties = ['Dairy', 'Meat', 'Bakery', 'Seafood', 'Beverage', '(Reserve)']

bars1 = ax1.bar(inspectors, loads, color=CATEGORICAL, edgecolor='white', linewidth=1.5)
ax1.set_ylabel('Facilities Assigned', fontsize=11)
ax1.set_title('Workload Distribution\n(Capacity: 3 per inspector)', fontsize=13, fontweight='bold')
ax1.axhline(y=3, color='gray', linestyle='--', linewidth=1, label='Max capacity (3)')
ax1.set_ylim(0, 4)

for bar, load, spec in zip(bars1, loads, specialties):
    label = '{} ({})'.format(load, spec) if load > 0 else 'Reserve'
    ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.1,
             label, ha='center', va='bottom', fontsize=9, fontweight='bold')

ax1.legend(fontsize=9)

# Right: Score contribution
bars2 = ax2.bar(inspectors, scores, color=CATEGORICAL, edgecolor='white', linewidth=1.5)
ax2.set_ylabel('Expertise Score Contribution', fontsize=11)
ax2.set_title('Expertise Score by Inspector\n(Total: 90/90 = Perfect Match)', fontsize=13, fontweight='bold')
ax2.set_ylim(0, 22)

for bar, score in zip(bars2, scores):
    if score > 0:
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                 '{} (9+9)'.format(score), ha='center', va='bottom', fontsize=9, fontweight='bold')
    else:
        ax2.text(bar.get_x() + bar.get_width() / 2, 0.5,
                 'Unassigned', ha='center', va='bottom', fontsize=9, color='gray')

plt.tight_layout()
plt.savefig('viz_workload_expertise.png', dpi=150, bbox_inches='tight')
print("Saved: viz_workload_expertise.png")
plt.close()

print("\nAll 3 visualizations generated successfully.")

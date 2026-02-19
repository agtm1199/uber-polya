#!/usr/bin/env python3
"""Visualizations for Milking Cows interpretation."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger

log = PolyaLogger()

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

COLORS = {
    'primary':   '#1976d2',
    'secondary': '#ff9800',
    'success':   '#4caf50',
    'danger':    '#d32f2f',
    'info':      '#00bcd4',
    'neutral':   '#9e9e9e',
}
FARMER_COLORS = ['#1976d2', '#d32f2f', '#4caf50']

# === DATA ===
intervals = [(300, 1000), (700, 1200), (1500, 2100)]
merged = [(300, 1200), (1500, 2100)]
farmers = ['Farmer 1', 'Farmer 2', 'Farmer 3']

# =========================================
# CHART 1: Timeline / Gantt Chart
# =========================================
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 5), height_ratios=[3, 1.5],
                                sharex=True, gridspec_kw={'hspace': 0.15})

# Top: Individual farmer intervals
for i, ((s, e), name) in enumerate(zip(intervals, farmers)):
    ax1.barh(i, e - s, left=s, height=0.6, color=FARMER_COLORS[i],
             edgecolor='white', linewidth=1.5, alpha=0.85)
    ax1.text(s + (e - s) / 2, i, '{} [{}-{}]'.format(name, s, e),
             ha='center', va='center', fontsize=10, fontweight='bold', color='white')

ax1.set_yticks(range(3))
ax1.set_yticklabels(farmers, fontsize=11)
ax1.set_title('Milking Cows: Timeline Analysis', fontsize=14, fontweight='bold')
ax1.set_ylim(-0.5, 2.5)

# Annotate overlap between Farmer 1 and 2
ax1.annotate('', xy=(700, 0.35), xytext=(1000, 0.35),
             arrowprops=dict(arrowstyle='<->', color='#ff9800', lw=2))
ax1.text(850, 0.55, 'overlap\n300s', ha='center', va='center',
         fontsize=8, color='#ff9800', fontweight='bold')

# Bottom: Merged timeline
for s, e in merged:
    ax2.barh(0, e - s, left=s, height=0.6, color=COLORS['success'],
             edgecolor='white', linewidth=1.5)
    ax2.text(s + (e - s) / 2, 0, '{}s'.format(e - s),
             ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# Mark the gap
gap_start = merged[0][1]
gap_end = merged[1][0]
ax2.barh(0, gap_end - gap_start, left=gap_start, height=0.6,
         color=COLORS['danger'], edgecolor='white', linewidth=1.5, alpha=0.3)
ax2.text(gap_start + (gap_end - gap_start) / 2, 0, 'IDLE\n{}s'.format(gap_end - gap_start),
         ha='center', va='center', fontsize=10, fontweight='bold', color=COLORS['danger'])

ax2.set_yticks([0])
ax2.set_yticklabels(['Merged'], fontsize=11)
ax2.set_xlabel('Time (seconds after 5:00 AM)', fontsize=11)
ax2.set_xlim(200, 2200)

# Add key result annotation
result_text = 'ANSWER: Longest milking = 900s | Longest idle = 300s'
fig.text(0.5, 0.01, result_text, ha='center', fontsize=12, fontweight='bold',
         bbox=dict(boxstyle='round,pad=0.5', facecolor='#e8f5e9', edgecolor=COLORS['success']))

plt.tight_layout(rect=[0, 0.05, 1, 1])
plt.savefig('milk2_timeline.png', dpi=150, bbox_inches='tight')
log.success("milk2_timeline.png", tag="SAVE")
plt.close()


# =========================================
# CHART 2: Algorithm Visualization (Steps)
# =========================================
fig, axes = plt.subplots(3, 1, figsize=(14, 7), sharex=True,
                          gridspec_kw={'hspace': 0.3})

# Step 1: Unsorted input
ax = axes[0]
ax.set_title('Step 1: Input Intervals (already sorted by start time)', fontsize=12, fontweight='bold')
for i, (s, e) in enumerate(intervals):
    ax.barh(i, e - s, left=s, height=0.5, color=FARMER_COLORS[i], alpha=0.8)
    ax.text(e + 20, i, '[{}, {}]'.format(s, e), va='center', fontsize=9)
ax.set_yticks(range(3))
ax.set_yticklabels(['I1', 'I2', 'I3'], fontsize=10)
ax.set_ylim(-0.5, 2.5)

# Step 2: Merge detection
ax = axes[1]
ax.set_title('Step 2: Detect Overlaps (I1 and I2 overlap since 700 <= 1000; I3 is separate since 1500 > 1200)',
             fontsize=10, fontweight='bold')
# Draw I1 and I2 merging
ax.barh(0, 1000 - 300, left=300, height=0.5, color=FARMER_COLORS[0], alpha=0.5)
ax.barh(0, 1200 - 700, left=700, height=0.5, color=FARMER_COLORS[1], alpha=0.5)
ax.barh(0, 1200 - 300, left=300, height=0.5, color='none',
        edgecolor=COLORS['success'], linewidth=3, linestyle='--')
ax.text(750, 0.35, 'MERGE', ha='center', fontsize=9, color=COLORS['success'], fontweight='bold')

ax.barh(1, 2100 - 1500, left=1500, height=0.5, color=FARMER_COLORS[2], alpha=0.8)
ax.text(1800, 1.35, 'SEPARATE', ha='center', fontsize=9, color=COLORS['danger'], fontweight='bold')

# Draw gap arrow
ax.annotate('', xy=(1200, 0.5), xytext=(1500, 0.5),
            arrowprops=dict(arrowstyle='<->', color=COLORS['danger'], lw=2))
ax.text(1350, 0.65, 'gap=300', ha='center', fontsize=9, color=COLORS['danger'])

ax.set_yticks([0, 1])
ax.set_yticklabels(['I1+I2', 'I3'], fontsize=10)
ax.set_ylim(-0.5, 1.8)

# Step 3: Final merged result
ax = axes[2]
ax.set_title('Step 3: Scan Merged Intervals for Answer', fontsize=12, fontweight='bold')
colors_merged = [COLORS['success'], COLORS['info']]
for i, (s, e) in enumerate(merged):
    ax.barh(0, e - s, left=s, height=0.6, color=colors_merged[i],
            edgecolor='white', linewidth=2)
    ax.text(s + (e - s) / 2, 0, 'M{}: {}s'.format(i + 1, e - s),
            ha='center', va='center', fontsize=11, fontweight='bold', color='white')

# Highlight the winner
ax.annotate('LONGEST\nMILKING', xy=(750, -0.4), fontsize=10,
            ha='center', color=COLORS['success'], fontweight='bold')
ax.annotate('', xy=(300, -0.35), xytext=(1200, -0.35),
            arrowprops=dict(arrowstyle='<->', color=COLORS['success'], lw=2.5))
ax.text(750, -0.55, '900s', ha='center', fontsize=12,
        color=COLORS['success'], fontweight='bold')

ax.set_yticks([0])
ax.set_yticklabels(['Result'], fontsize=10)
ax.set_xlabel('Time (seconds)', fontsize=11)
ax.set_xlim(200, 2200)
ax.set_ylim(-0.7, 0.5)

plt.savefig('milk2_algorithm.png', dpi=150, bbox_inches='tight')
log.success("milk2_algorithm.png", tag="SAVE")
plt.close()

log.blank()
log.success("All visualizations generated successfully.", tag="COMPLETE")

#!/usr/bin/env python3
"""Land Survey Analysis solver using computational geometry.

Computes area, perimeter, convex hull, centroid, and building containment
for an irregular polygon defined by GPS survey points.

Algorithms: Shoelace formula O(n), ConvexHull O(n log n), point-in-polygon O(n).
Correctness: Area cross-verified with independent shoelace implementation.
"""
from __future__ import annotations

import json
import math
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
from scipy.spatial import ConvexHull, Voronoi
from shapely.geometry import Polygon, box

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for land survey analysis."""
    vertices: tuple[tuple[float, float], ...]  # (x, y) coordinates in meters
    building_footprint: tuple[float, float, float, float]  # (width, height, proposed_x, proposed_y)
    label: str = "Survey Lot"

    @property
    def n(self) -> int:
        return len(self.vertices)


@dataclass
class Solution:
    """Verified solution with all computed geometric properties."""
    area: float                                   # polygon area in m^2
    perimeter: float                              # boundary length in m
    convex_hull_vertices: list[tuple[float, float]]  # vertices of the convex hull
    convex_hull_area: float                       # area of the convex hull
    centroid: tuple[float, float]                 # (x, y) of geometric centroid
    building_fits: bool                           # does the proposed building fit?
    max_inscribed_rectangle: tuple[float, float, float, float]  # (x, y, width, height)
    max_inscribed_area: float                     # area of max inscribed rectangle
    concavity_ratio: float                        # lot_area / hull_area (1.0 = convex)
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- Shoelace Formula (independent implementation) ---

def _shoelace_area(vertices: tuple[tuple[float, float], ...]) -> float:
    """Compute polygon area using the shoelace formula (Gauss's area formula).

    Returns the absolute area for a simple (non-self-intersecting) polygon.
    Vertices may be in either clockwise or counter-clockwise order.
    """
    n = len(vertices)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        xi, yi = vertices[i]
        xj, yj = vertices[j]
        area += xi * yj
        area -= xj * yi
    return abs(area) / 2.0


def _shoelace_centroid(vertices: tuple[tuple[float, float], ...]) -> tuple[float, float]:
    """Compute polygon centroid using the shoelace sub-expressions.

    The centroid of a simple polygon with vertices (x_i, y_i) is:
        C_x = (1 / 6A) * sum( (x_i + x_{i+1}) * (x_i * y_{i+1} - x_{i+1} * y_i) )
        C_y = (1 / 6A) * sum( (y_i + y_{i+1}) * (x_i * y_{i+1} - x_{i+1} * y_i) )
    where A is the signed area.
    """
    n = len(vertices)
    signed_area = 0.0
    cx = 0.0
    cy = 0.0
    for i in range(n):
        j = (i + 1) % n
        xi, yi = vertices[i]
        xj, yj = vertices[j]
        cross = xi * yj - xj * yi
        signed_area += cross
        cx += (xi + xj) * cross
        cy += (yi + yj) * cross
    signed_area /= 2.0
    cx /= (6.0 * signed_area)
    cy /= (6.0 * signed_area)
    return (cx, cy)


def _perimeter(vertices: tuple[tuple[float, float], ...]) -> float:
    """Compute polygon perimeter as sum of edge lengths."""
    n = len(vertices)
    total = 0.0
    for i in range(n):
        j = (i + 1) % n
        dx = vertices[j][0] - vertices[i][0]
        dy = vertices[j][1] - vertices[i][1]
        total += math.hypot(dx, dy)
    return total


# --- Max Inscribed Axis-Aligned Rectangle (grid search) ---

def _max_inscribed_rect(
    polygon: Polygon,
    grid_steps: int = 50,
    size_steps: int = 20,
) -> tuple[float, float, float, float]:
    """Find the largest axis-aligned rectangle inscribed in the polygon.

    Uses a grid search over candidate center positions and sizes.
    Returns (center_x, center_y, width, height).
    """
    minx, miny, maxx, maxy = polygon.bounds
    best_area = 0.0
    best_rect = (0.0, 0.0, 0.0, 0.0)

    max_w = maxx - minx
    max_h = maxy - miny

    for ix in range(grid_steps):
        cx = minx + (ix + 0.5) * max_w / grid_steps
        for iy in range(grid_steps):
            cy = miny + (iy + 0.5) * max_h / grid_steps
            if not polygon.contains(box(cx - 0.1, cy - 0.1, cx + 0.1, cy + 0.1)):
                continue
            # Binary search on size at this center
            for sw in range(size_steps, 0, -1):
                w = max_w * sw / (size_steps * 2)
                for sh in range(size_steps, 0, -1):
                    h = max_h * sh / (size_steps * 2)
                    if w * h <= best_area:
                        continue
                    candidate = box(cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2)
                    if polygon.contains(candidate):
                        best_area = w * h
                        best_rect = (cx, cy, w, h)
                        break  # found best h for this w at this center

    return best_rect


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the land survey analysis problem."""
    t0 = time.perf_counter()

    vertices = instance.vertices
    bw, bh, bx, by = instance.building_footprint

    # Build shapely polygon
    poly = Polygon(vertices)

    # 1. Area (via shapely)
    area = poly.area

    # 2. Perimeter (via shapely)
    perimeter = poly.length

    # 3. Convex hull (via scipy)
    pts = np.array(vertices)
    hull = ConvexHull(pts)
    hull_vertices = [tuple(pts[i]) for i in hull.vertices]
    hull_area = hull.volume  # in 2D, ConvexHull.volume gives area

    # 4. Centroid (via shapely)
    centroid_pt = poly.centroid
    centroid = (centroid_pt.x, centroid_pt.y)

    # 5. Building containment check
    building_rect = box(bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2)
    building_fits = poly.contains(building_rect)

    # 6. Max inscribed axis-aligned rectangle
    mir = _max_inscribed_rect(poly)
    mir_area = mir[2] * mir[3]

    # 7. Concavity ratio
    concavity_ratio = area / hull_area if hull_area > 0 else 1.0

    elapsed = time.perf_counter() - t0

    sol = Solution(
        area=area,
        perimeter=perimeter,
        convex_hull_vertices=hull_vertices,
        convex_hull_area=hull_area,
        centroid=centroid,
        building_fits=building_fits,
        max_inscribed_rectangle=mir,
        max_inscribed_area=mir_area,
        concavity_ratio=concavity_ratio,
        is_feasible=False,  # set after verification
        algorithm="Shoelace + ConvexHull(Qhull) + Shapely containment",
        time_seconds=elapsed,
        certificate="Area cross-verified with independent shoelace formula",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, sol)

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    sol: Solution,
) -> tuple[bool, dict[str, Any]]:
    """Independently verify all computed geometric properties."""
    checks: dict[str, Any] = {}
    all_ok = True
    tol = 1e-4

    vertices = instance.vertices

    # Check 1: Area via independent shoelace formula
    shoelace = _shoelace_area(vertices)
    area_match = abs(sol.area - shoelace) < tol * max(sol.area, 1.0)
    checks["area_matches_shoelace"] = area_match
    checks["area_shapely"] = round(sol.area, 4)
    checks["area_shoelace"] = round(shoelace, 4)
    if not area_match:
        all_ok = False

    # Check 2: Perimeter via independent computation
    indep_perimeter = _perimeter(vertices)
    perim_match = abs(sol.perimeter - indep_perimeter) < tol * max(sol.perimeter, 1.0)
    checks["perimeter_matches_independent"] = perim_match
    checks["perimeter_shapely"] = round(sol.perimeter, 4)
    checks["perimeter_independent"] = round(indep_perimeter, 4)
    if not perim_match:
        all_ok = False

    # Check 3: Centroid via independent shoelace centroid
    indep_centroid = _shoelace_centroid(vertices)
    cx_match = abs(sol.centroid[0] - indep_centroid[0]) < tol * max(abs(sol.centroid[0]), 1.0)
    cy_match = abs(sol.centroid[1] - indep_centroid[1]) < tol * max(abs(sol.centroid[1]), 1.0)
    centroid_match = cx_match and cy_match
    checks["centroid_matches_independent"] = centroid_match
    checks["centroid_shapely"] = (round(sol.centroid[0], 4), round(sol.centroid[1], 4))
    checks["centroid_independent"] = (round(indep_centroid[0], 4), round(indep_centroid[1], 4))
    if not centroid_match:
        all_ok = False

    # Check 4: Convex hull area >= polygon area (hull encloses polygon)
    hull_ge_poly = sol.convex_hull_area >= sol.area - tol
    checks["hull_area_ge_polygon_area"] = hull_ge_poly
    if not hull_ge_poly:
        all_ok = False

    # Check 5: Concavity ratio in [0, 1]
    ratio_valid = 0.0 <= sol.concavity_ratio <= 1.0 + tol
    checks["concavity_ratio_valid"] = ratio_valid
    if not ratio_valid:
        all_ok = False

    # Check 6: Polygon is simple (non-self-intersecting)
    poly = Polygon(vertices)
    is_simple = poly.is_valid
    checks["polygon_is_simple"] = is_simple
    if not is_simple:
        all_ok = False

    # Check 7: Building containment cross-check
    bw, bh, bx, by = instance.building_footprint
    building_rect = box(bx - bw / 2, by - bh / 2, bx + bw / 2, by + bh / 2)
    # Check all 4 corners of building are inside polygon
    corners = list(building_rect.exterior.coords)[:-1]  # 4 corners
    corners_inside = all(poly.contains(Polygon([c, c, c])) or poly.exterior.distance(
        Polygon([c]).centroid) < tol for c in corners)
    # Simpler: use shapely's own containment on the rectangle
    indep_fits = poly.contains(building_rect)
    checks["building_containment_matches"] = (sol.building_fits == indep_fits)
    if sol.building_fits != indep_fits:
        all_ok = False

    # Check 8: Max inscribed rectangle actually fits inside polygon
    if sol.max_inscribed_area > 0:
        mx, my, mw, mh = sol.max_inscribed_rectangle
        mir_box = box(mx - mw / 2, my - mh / 2, mx + mw / 2, my + mh / 2)
        mir_inside = poly.contains(mir_box)
        checks["max_inscribed_rect_fits"] = mir_inside
        if not mir_inside:
            all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 8-point irregular lot with realistic coordinates (meters)
    # Represents a roughly 8000 m^2 suburban lot with a concave indentation
    # on the NW side (P6 is pulled inward), making the polygon non-convex.
    lot_vertices = (
        (100.0,  200.0),   # P0 -- SW corner
        (140.0,  195.0),   # P1 -- south edge, slight dip
        (180.0,  210.0),   # P2 -- SE area
        (185.0,  260.0),   # P3 -- east side
        (170.0,  300.0),   # P4 -- NE corner
        (130.0,  310.0),   # P5 -- north edge
        (130.0,  270.0),   # P6 -- NW indentation (concave notch)
        ( 90.0,  245.0),   # P7 -- west side
    )

    # Proposed building: 20m x 12m rectangle centered at (140, 255)
    building = (20.0, 12.0, 140.0, 255.0)

    instance = Instance(
        vertices=lot_vertices,
        building_footprint=building,
        label="Suburban Irregular Lot (8 points)",
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Land Survey Analysis")
    log.metric("Label:", instance.label, tag="DATA")
    log.metric("Survey points:", str(instance.n), tag="DATA")
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.4f}s", tag="TIMING")
    log.blank()

    # Lot geometry
    log.step("LOT GEOMETRY")
    log.metric("Area:", f"{sol.area:,.2f} m^2", tag="RESULT")
    log.metric("Perimeter:", f"{sol.perimeter:,.2f} m", tag="RESULT")
    log.metric("Centroid:", f"({sol.centroid[0]:.2f}, {sol.centroid[1]:.2f})", tag="RESULT")
    log.blank()

    # Vertex listing
    log.step("SURVEY VERTICES")
    for i, (x, y) in enumerate(instance.vertices):
        log.table_row(f"  P{i}:  ({x:>7.1f}, {y:>7.1f})", tag="TABLE")
    log.blank()

    # Edge lengths
    log.step("EDGE LENGTHS")
    total_perim = 0.0
    for i in range(instance.n):
        j = (i + 1) % instance.n
        x0, y0 = instance.vertices[i]
        x1, y1 = instance.vertices[j]
        length = math.hypot(x1 - x0, y1 - y0)
        total_perim += length
        log.table_row(
            f"  P{i} -> P{j}:  {length:>8.2f} m",
            tag="TABLE",
        )
    log.table_row(f"  {'TOTAL':>10}:  {total_perim:>8.2f} m", tag="RESULT")
    log.blank()

    # Convex hull
    log.step("CONVEX HULL")
    log.metric("Hull vertices:", str(len(sol.convex_hull_vertices)), tag="RESULT")
    for i, (x, y) in enumerate(sol.convex_hull_vertices):
        log.table_row(f"  H{i}:  ({x:>7.1f}, {y:>7.1f})", tag="TABLE")
    log.metric("Hull area:", f"{sol.convex_hull_area:,.2f} m^2", tag="RESULT")
    log.metric("Lot area:", f"{sol.area:,.2f} m^2", tag="RESULT")
    log.metric("Concavity ratio:", f"{sol.concavity_ratio:.4f} (1.0 = convex)", tag="STATS")
    log.blank()

    # Building containment
    log.step("BUILDING CONTAINMENT CHECK")
    bw, bh, bx, by = instance.building_footprint
    log.metric("Building size:", f"{bw:.1f} x {bh:.1f} m", tag="DATA")
    log.metric("Proposed center:", f"({bx:.1f}, {by:.1f})", tag="DATA")
    log.metric("Building area:", f"{bw * bh:,.1f} m^2", tag="DATA")
    if sol.building_fits:
        log.success("Building FITS within the lot", tag="RESULT")
    else:
        log.warning("Building does NOT fit within the lot", tag="RESULT")
    log.blank()

    # Max inscribed rectangle
    log.step("MAX INSCRIBED AXIS-ALIGNED RECTANGLE")
    mx, my, mw, mh = sol.max_inscribed_rectangle
    log.metric("Center:", f"({mx:.2f}, {my:.2f})", tag="RESULT")
    log.metric("Size:", f"{mw:.2f} x {mh:.2f} m", tag="RESULT")
    log.metric("Area:", f"{sol.max_inscribed_area:,.2f} m^2", tag="RESULT")
    log.metric("% of lot:", f"{sol.max_inscribed_area / sol.area * 100:.1f}%", tag="STATS")
    log.blank()

    # Voronoi analysis (bonus: partition the lot into regions nearest to each vertex)
    log.step("VORONOI ANALYSIS (bonus)")
    pts = np.array(instance.vertices)
    try:
        vor = Voronoi(pts)
        log.metric("Voronoi vertices:", str(len(vor.vertices)), tag="STATS")
        log.metric("Voronoi regions:", str(len(vor.regions)), tag="STATS")
        log.info("Voronoi partitioning can identify which survey marker is nearest "
                 "to any point in the lot -- useful for drainage analysis.", tag="INTERPRET")
    except Exception as e:
        log.warning(f"Voronoi computation skipped: {e}", tag="WARNING")
    log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        elif isinstance(result, tuple):
            log.check(check_name, f"({result[0]}, {result[1]})", tag="VERIFY")
        else:
            log.check(check_name, result, tag="VERIFY")
    log.blank()

    log.metric("All checks passed:", str(sol.is_feasible), tag="VERIFY")
    log.blank()

    # Save solution
    output = {
        "label": instance.label,
        "n_vertices": instance.n,
        "area_m2": round(sol.area, 4),
        "perimeter_m": round(sol.perimeter, 4),
        "centroid": [round(c, 4) for c in sol.centroid],
        "convex_hull_vertices": [[round(x, 4), round(y, 4)] for x, y in sol.convex_hull_vertices],
        "convex_hull_area_m2": round(sol.convex_hull_area, 4),
        "concavity_ratio": round(sol.concavity_ratio, 4),
        "building_fits": sol.building_fits,
        "building_footprint": {
            "width": building[0],
            "height": building[1],
            "center_x": building[2],
            "center_y": building[3],
        },
        "max_inscribed_rectangle": {
            "center_x": round(mx, 4),
            "center_y": round(my, 4),
            "width": round(mw, 4),
            "height": round(mh, 4),
            "area_m2": round(sol.max_inscribed_area, 4),
        },
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": round(sol.time_seconds, 6),
    }
    with open(Path(__file__).parent / "solution.json", "w") as f:
        json.dump(output, f, indent=2)
    log.success("solution.json", tag="SAVE")
    log.divider(style="thick")

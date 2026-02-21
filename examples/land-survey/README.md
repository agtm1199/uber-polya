# Land Survey Analysis

**Domain**: Computational Geometry
**Algorithm**: Shoelace formula, convex hull (scipy.spatial), point-in-polygon (shapely)
**Key Concepts**: Computational geometry, polygon operations, spatial containment, Voronoi partitioning

## Problem

A surveyor has recorded GPS coordinates for 8 boundary markers defining an irregular lot. Given these coordinates (in meters, local projected coordinate system), compute:

1. **Area** of the lot polygon
2. **Perimeter** of the lot boundary
3. **Convex hull** of the survey points
4. **Centroid** (geometric center of mass)
5. **Building fit check** -- determine whether a proposed rectangular building footprint fits entirely within the lot

The lot is an irregular 8-sided polygon. The building footprint is an axis-aligned rectangle placed at a proposed location. The solver must verify containment using independent geometric methods.

## Files

| File | Description |
|------|-------------|
| `survey_solver.py` | Full solver with area, perimeter, convex hull, centroid, containment check, and independent verification |

## Requirements

```bash
pip install shapely scipy numpy
```

## Quick Run

```bash
python3 survey_solver.py
```

## Expected Output

- Lot area computed via shapely and independently verified with the shoelace formula
- Perimeter of the lot boundary
- Convex hull vertices and hull area (compared to lot area for concavity measure)
- Centroid coordinates
- Building containment verdict (fits / does not fit)
- Maximum axis-aligned inscribed rectangle estimate
- Independent verification of all computed quantities

## Algorithm

1. **Area**: Shoelace formula (Gauss's area formula) for simple polygons -- O(n)
2. **Perimeter**: Sum of Euclidean distances between consecutive vertices -- O(n)
3. **Convex hull**: Scipy `ConvexHull` (Qhull library, O(n log n))
4. **Centroid**: Weighted average using the shoelace sub-expressions -- O(n)
5. **Containment**: Shapely `Polygon.contains()` for the full building rectangle -- O(n) per query
6. **Max inscribed rectangle**: Grid search over candidate positions and sizes within the polygon

## Key Concepts

- **Computational geometry** -- algorithms operating on points, lines, and polygons in the plane
- **Polygon operations** -- area, perimeter, convex hull, centroid for arbitrary simple polygons
- **Spatial containment** -- testing whether one geometric object lies entirely within another
- **Voronoi partitioning** -- dual of Delaunay triangulation, useful for nearest-facility analysis
- **Shoelace formula** -- exact O(n) area computation for simple polygons from vertex coordinates
- **Convex hull** -- smallest convex set containing all points; measures lot "regularity"

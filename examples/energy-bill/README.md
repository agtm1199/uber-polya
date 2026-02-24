# Energy Bill Optimization

## Problem

Schedule 5 household appliances (dishwasher, washer, dryer, EV charger, pool pump)
across a 24-hour day to minimize daily electricity cost under time-of-use pricing.
Each appliance runs once daily for a fixed duration at a fixed power draw.
Some appliances (washer, dryer) cannot run overnight due to noise constraints.

## Rate Structure

| Tier     | Hours          | Rate ($/kWh) |
|----------|----------------|--------------|
| Off-peak | 11pm -- 7am    | $0.08        |
| Mid-peak | 7am -- 4pm, 9pm -- 11pm | $0.15 |
| Peak     | 4pm -- 9pm     | $0.30        |

## Appliances

| Appliance   | Duration | Power  | kWh/run | Constraint         |
|-------------|----------|--------|---------|--------------------|
| Dishwasher  | 2 hr     | 1.8 kW | 3.6    | None (runs anytime)|
| Washer      | 1 hr     | 0.5 kW | 0.5    | Daytime only (7am--10pm) |
| Dryer       | 2 hr     | 5.0 kW | 10.0   | Daytime only (7am--10pm) |
| EV Charger  | 4 hr     | 7.2 kW | 28.8   | None (runs anytime)|
| Pool Pump   | 6 hr     | 1.1 kW | 6.6    | None (runs anytime)|

## Files

| File | Description |
|------|-------------|
| `energy_solver.py` | ILP solver using PuLP/CBC with independent verification |
| `solution.json`    | Solver output: schedule, costs, and savings comparison |

## Requirements

```bash
pip install pulp
```

## Quick Run

```bash
python3 energy_solver.py
```

## Expected Output

- Optimal start hour for each appliance
- Per-appliance cost breakdown
- 24-hour visual timeline showing appliance scheduling vs rate tiers
- Comparison against worst-case (all peak) and naive (typical daytime) schedules
- Monthly and annual projected savings
- Independent constraint verification (all PASS)

## Algorithm

Integer Linear Programming (ILP) via PuLP/CBC.

- **Binary variables**: x[appliance, start_hour] = 1 if appliance starts at that hour
- **Objective**: minimize sum over all appliance-hours of (power_kw * rate_at_hour)
- **Constraints**: each appliance starts exactly once, within its allowed hours, and finishes within the 24-hour window
- **Result**: exact global optimum via Branch & Bound

## Key Concepts

- **Time-of-use pricing** -- electricity costs vary by hour; shifting loads to off-peak saves money
- **Binary assignment ILP** -- each appliance-start is a binary decision variable
- **Noise constraints** -- washer and dryer restricted to daytime hours, modeled as allowed start hour sets
- **Independent verification** -- 6 checks (all scheduled, allowed hours, window fit, overlap analysis, cost recomputation, valid ranges) run outside the solver
- **Savings analysis** -- optimal vs naive vs worst-case cost comparison with monthly/annual projections

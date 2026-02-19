# Fair Rent Division

## Problem

Three roommates (Alice, Bob, Carol) share an apartment with 3 rooms of different
sizes (master 150 sqft, medium 120 sqft, small 90 sqft). Total rent is $3000/month.
Each person privately bids what fraction of rent each room is worth to them. Find a
fair allocation: who gets which room and pays how much, so that no one envies another.

## Files

| File | Description |
|------|-------------|
| `rent_solver.py` | Fair division solver using proportional bidding and envy-free adjustment |

## Requirements

```bash
pip install scipy
```

## Quick Run

```bash
python3 rent_solver.py
```

## Expected Output

- Room assignment for each roommate
- Rent payment for each roommate (summing to $3000)
- Envy-freeness verification (no roommate prefers another's deal)
- Proportionality verification (each roommate gets at least 1/3 of their value)

## Algorithm

Proportional fair division with envy-free rent splitting.

- Each roommate bids their valuation for each room
- Optimal assignment maximizes total welfare (sum of valuations)
- Rent is split proportionally to bids, then adjusted for envy-freeness
- Uses scipy.optimize.linear_sum_assignment for optimal matching

## Key Concepts

- **Fair division** -- allocating indivisible goods with monetary transfers
- **Envy-freeness** -- no participant prefers another's allocation at their price
- **Proportionality** -- each participant values their bundle at >= 1/n of total
- **Welfare maximization** -- assignment that maximizes total reported satisfaction

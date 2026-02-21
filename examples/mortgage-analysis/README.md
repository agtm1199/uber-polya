# Mortgage Comparison Analysis

**Domain**: Financial Mathematics (Time Value of Money)
**Algorithm**: NPV, PMT, amortization schedule, break-even analysis (numpy-financial)
**Key Concepts**: Time value of money, amortization, refinancing break-even, total interest comparison

## Problem

A homebuyer is purchasing a $400,000 home with an $80,000 down payment ($320,000 loan). Compare three mortgage options:

1. **30-year fixed** at 6.5% APR
2. **15-year fixed** at 5.8% APR
3. **Refinance scenario**: Start with the 30-year at 6.5%, then after 5 years refinance the remaining balance into a new 25-year loan at 5.2% APR with $6,000 in closing costs

Which option minimizes total cost? When does refinancing break even against staying with the original 30-year loan?

## Files

| File | Description |
|------|-------------|
| `mortgage_solver.py` | Full solver with amortization schedules, cost comparison, refinance break-even analysis, and independent verification |

## Requirements

```bash
pip install numpy numpy-financial
```

## Quick Run

```bash
python3 mortgage_solver.py
```

## Expected Output

- Monthly payments for each option
- Full amortization schedule summaries (total interest, total paid)
- Refinance break-even month (when cumulative savings exceed closing costs)
- Net savings from refinancing over the remaining loan life
- Independent verification that amortization schedules sum correctly

## Algorithm

1. **PMT calculation**: Compute monthly payment using the annuity formula P = L * r(1+r)^n / ((1+r)^n - 1)
2. **Amortization schedule**: For each month, split payment into principal and interest, track remaining balance
3. **Refinance analysis**: After 60 months on the 30-year loan, compute remaining balance, then start a new 25-year schedule at the lower rate plus closing costs
4. **Break-even**: Find the month where cumulative payment savings from refinancing exceed the closing costs
5. **Verify**: Independently confirm that principal payments sum to the loan amount and that final balances are zero

## Key Concepts

- **Time value of money** -- future dollars are worth less than present dollars; interest rates quantify this
- **Amortization** -- spreading a loan into equal periodic payments that cover both interest and principal
- **Refinancing break-even** -- the point at which lower monthly payments recover the upfront closing costs
- **Total interest comparison** -- the true cost difference between loan options beyond just the monthly payment
- **APR to monthly rate** -- dividing annual percentage rate by 12 for monthly compounding

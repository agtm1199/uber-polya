# Every Problem Is a Math Problem

## You just don't know it yet.

You have a scheduling conflict. You need to split costs fairly. You're deciding which projects to fund. You're routing deliveries. You're figuring out whether that A/B test result is real or noise.

These feel like different problems. They're not. They all have the same shape:

**Given some constraints, find the best answer.**

That's a math problem. And math problems have solvers.

---

## The Hidden Structure

Every hard decision you make is secretly one of a small number of mathematical structures wearing a real-world disguise.

"Schedule 12 nurses across 3 shifts so nobody works more than 5 days" is not a scheduling problem. It is an integer linear program with 252 binary variables and 48 constraints. It has an optimal solution. A solver can find it in 0.3 seconds and prove that no better answer exists.

"Split rent fairly among 3 roommates with different-sized rooms" is not a negotiation. It is a fair division problem with well-studied mathematical properties. There exists a provably fair allocation. An algorithm can compute it.

"Pick the best 5 of 20 projects given a $500K budget" is not a meeting. It is a knapsack optimization. The combination that maximizes total value under the budget constraint is computable. And the solver can tell you exactly how much value you'd lose by picking differently.

You don't need to know any of this to solve these problems. You just need a tool that does.

---

## The Gap

Today, when people face hard decisions, they do one of four things:

**They wing it.** Gut feeling, experience, intuition. Sometimes right. No way to know when it's wrong. No way to know how much you left on the table.

**They use spreadsheets.** Works for simple problems. Falls apart the moment you have more than a few constraints or the search space is combinatorial. You can't brute-force a scheduling problem with 252 variables in a spreadsheet.

**They ask AI.** ChatGPT or Claude gives you a plausible-sounding answer. But it's not verified. It might be wrong. It might be suboptimal. There's no proof, no sensitivity analysis, no optimality certificate. The AI sounds confident whether or not it's right.

**They hire a consultant.** Expensive, slow, and the model lives in their head. When the inputs change next month, you need them again.

All four approaches share the same flaw: **they skip the modeling step.** They jump from "I have a problem" to "here's an answer" without ever formalizing what the problem actually is.

The modeling step is where all the value lives.

---

## What Modeling Does

When you formalize a problem into a mathematical model, three things happen:

**1. Ambiguity disappears.** "Schedule the nurses fairly" is vague. "Minimize the maximum number of shifts assigned to any single nurse, subject to: each shift has at least 4 nurses, no nurse works more than 5 days, and these 3 nurses can't work nights" is precise. The act of modeling forces you to decide what you actually mean.

**2. The solution space becomes searchable.** Once you have a formal model, algorithms can explore millions of possible solutions in seconds. Not by guessing -- by exploiting mathematical structure. A branch-and-bound solver doesn't try every combination. It provably eliminates vast regions of the search space that can't contain the optimum.

**3. The answer comes with a guarantee.** A verified solution tells you not just "here's a good answer" but "here's the best possible answer, and here's the proof." Or: "here's an answer within 5% of optimal, and that's the best anyone can do in polynomial time for this class of problem." You know exactly what you're getting.

---

## Polya's Insight

In 1945, mathematician George Polya published *How to Solve It* -- a slim book that articulated a universal method for solving mathematical problems. Not a method for solving equations. A method for solving *problems*.

His four phases:

1. **Understand the problem.** What is the unknown? What are the data? What are the conditions? Can you restate it in your own words?

2. **Devise a plan.** Have you seen a similar problem? Do you know a related result? Can you solve a simpler version first? Can you break it into parts?

3. **Execute the plan.** Carry it out step by step. Check each step as you go. Can you prove that each step is correct?

4. **Look back.** Can you check the result? Can you derive it differently? Can you use the result or the method for some other problem?

This method is 80 years old. It works for every mathematical problem, from arithmetic to topology. But it was designed for humans with pencils and paper.

We now have something Polya didn't: AI that understands natural language, solver libraries that can process millions of variables in seconds, and verification methods that can prove answers are correct.

---

## The Universal Algorithm

uber-polya connects Polya's universal method to modern computational tools. It is a meta-algorithm: an algorithm that selects and orchestrates the right algorithm for any problem.

```
Input:  a problem (described in natural language)

UBER-POLYA(problem):
  1. UNDERSTAND  -- Socratic dialogue: extract unknowns, data, constraints
  2. CLASSIFY    -- Map to a mathematical structure (graph, ILP, distribution, ...)
  3. SELECT      -- Pick the right algorithm for that structure and instance size
  4. EXECUTE     -- Run it, verify independently, compute optimality certificate
  5. INTERPRET   -- Translate back to real-world answer with sensitivity analysis

Output: a verified solution (in whatever form you need)
```

This is a compiler for problems. It compiles human problems into mathematical programs, executes them, and decompiles the results back into human answers.

The classification step is the key. There are roughly 50 named problem classes that cover most real-world computational problems: graph coloring, shortest path, bipartite matching, knapsack, set cover, ILP, satisfiability, hypothesis testing, regression, fair division, convex optimization, and so on. Each has known algorithms with known complexity, known approximation guarantees, and established solver libraries.

Most people never find their way to these problem classes because the mapping from "schedule my nurses" to "integer linear program" requires expertise that isn't widely held. uber-polya provides that mapping through Socratic dialogue. It asks the questions Polya would ask -- questions that guide you from a vague problem statement to a precise formal model -- and then it solves the model with the right tool.

---

## What This Means in Practice

**For the operations manager** who spends 6 hours every month building the shift schedule by hand: uber-polya formalizes it as an ILP, solves it in seconds, and proves the schedule is optimal. Every month, you type the updated constraints, and you get the best possible schedule. 6 hours becomes 2 minutes.

**For the startup founder** deciding which features to build next: uber-polya models it as a knapsack problem -- maximize user value subject to engineering capacity. Instead of an argument in a meeting, you get a ranked list with explicit trade-offs. "If you swap feature A for feature B, you lose 12% of expected value but free up 3 weeks of capacity."

**For the student** planning a study schedule: uber-polya models it as graph coloring. Subjects that share prerequisite knowledge get different time slots. The result is a weekly timetable that's provably conflict-free and balanced across subjects.

**For the data scientist** running an A/B test: uber-polya selects the right hypothesis test based on your data's distribution, computes the result three different ways (frequentist, Bayesian, and bootstrap), and tells you whether the effect is real -- with confidence intervals, power analysis, and a plain-English interpretation.

In every case, the user didn't need to know the math. They described their problem. uber-polya found the structure, selected the solver, ran it, verified the answer, and delivered the result.

---

## Why Verification Matters

LLMs are confident whether they're right or wrong. This is a known problem. In domains where correctness matters -- scheduling, allocation, financial decisions, statistical conclusions -- a confidently wrong answer is worse than no answer at all.

uber-polya doesn't trust itself. Every solution includes independent verification:

- **Feasibility check**: every constraint re-checked independently of the solver
- **Optimality certificate**: LP relaxation bounds, dual solutions, exhaustive comparison for small instances
- **Cross-validation**: when possible, solve the same problem with a different algorithm and compare
- **Sensitivity analysis**: perturb the inputs and see how the solution changes

When uber-polya says "this is optimal," there's a mathematical proof backing that claim. When it says "this is approximate," it tells you the approximation ratio and what that means.

This is the difference between "the AI says this is a good schedule" and "this schedule is mathematically proven to be the best one possible given your constraints."

---

## The Expansion

Polya's method is domain-independent. The four phases work for any mathematical problem. uber-polya started with discrete mathematics -- the domain with the cleanest complexity theory and most mature solver ecosystem -- and is expanding outward.

Today: discrete optimization, continuous optimization, statistical inference. 139 algorithms across 10 domains.

Coming: game theory, simulation, decision analysis, time series, machine learning, differential equations.

Each new domain extends the set of real-world problems uber-polya can solve. Game theory unlocks negotiation and strategy. Simulation unlocks "what are the odds?" and scenario planning. Decision analysis unlocks multi-criteria ranking and trade-off problems.

The goal is not to cover all of mathematics. The goal is to cover all of the mathematical structures that commonly appear in everyday problems. That set is finite and well-studied. We're building toward it.

---

## The Invitation

uber-polya is free, open-source, and available today. It works on Claude Code, Codex CLI, Cursor, and any platform that supports the Agent Skills standard.

If you have a problem you're solving by gut feel, spreadsheet, or unverified AI output -- try formalizing it. You might be surprised by what a solver can do with 0.3 seconds and a clear model.

Every problem has a mathematical structure. uber-polya finds it, solves it, and proves the answer is right.

One algorithm. Any problem.

---

*uber-polya is built on the work of George Polya (How to Solve It, 1945), the open-source solver ecosystem (NetworkX, PuLP, Z3, SymPy, SciPy, OR-Tools, cvxpy, statsmodels, PyMC), and the Anthropic Claude platform. It stands on the shoulders of giants.*

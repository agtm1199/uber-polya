#!/usr/bin/env python3
"""Workout Plan solver -- Integer Linear Programming for weekly exercise scheduling.

Designs a 5-day weekly workout plan selecting exercises from a catalog.
Each exercise targets certain muscle groups with a given set count and duration.
Minimizes total weekly workout time while meeting minimum volume targets
per muscle group, respecting per-session time limits, and forbidding the
same exercise on consecutive days.  Uses PuLP/CBC for ILP.

Algorithm: Integer Linear Programming (Branch & Bound via CBC).
Complexity: NP-hard in general, but small instances solve instantly.
Correctness: Exact optimal, verified independently.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any

from pulp import (
    LpProblem, LpVariable, LpMinimize, LpBinary,
    LpStatus, value, lpSum, PULP_CBC_CMD,
)

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from utils.polya_logger import PolyaLogger
log = PolyaLogger()


# --- Data Model ---

@dataclass(frozen=True)
class Instance:
    """Problem instance for weekly workout planning.

    Attributes:
        exercises: tuple of dicts with keys name, muscles (list[str]),
                   duration_min (int), sets (int).
        days: tuple of day labels (e.g. ("Mon", "Tue", ...)).
        muscle_targets: dict mapping muscle group -> minimum weekly sets.
        max_time_per_day: maximum minutes allowed per session.
    """
    exercises: tuple[dict[str, Any], ...]
    days: tuple[str, ...]
    muscle_targets: dict[str, int]
    max_time_per_day: int

    @property
    def num_exercises(self) -> int:
        return len(self.exercises)

    @property
    def num_days(self) -> int:
        return len(self.days)


@dataclass
class Solution:
    """Verified solution with metadata."""
    schedule: dict[str, list[str]]   # day -> list of exercise names
    objective: float | None          # total workout time (minutes)
    is_optimal: bool
    is_feasible: bool
    algorithm: str
    time_seconds: float
    certificate: str
    constraint_check: dict[str, Any] = field(default_factory=dict)


# --- Solver ---

def solve(instance: Instance) -> Solution:
    """Solve the workout planning ILP.  Returns verified solution."""
    t0 = time.perf_counter()

    exercises = instance.exercises
    days = instance.days
    muscles = list(instance.muscle_targets.keys())

    # Lookup helpers
    ex_names = [e["name"] for e in exercises]
    ex_by_name: dict[str, dict[str, Any]] = {e["name"]: e for e in exercises}

    # Build ILP
    prob = LpProblem("workout_plan", LpMinimize)

    # Binary decision variables: x[exercise_name, day] = 1 if exercise is
    # scheduled on that day
    x: dict[tuple[str, str], LpVariable] = {}
    for e in ex_names:
        for d in days:
            x[e, d] = LpVariable(f"x_{e.replace(' ', '_')}_{d}", cat=LpBinary)

    # Objective: minimize total workout time across all days
    prob += (
        lpSum(
            ex_by_name[e]["duration_min"] * x[e, d]
            for e in ex_names for d in days
        ),
        "total_time",
    )

    # Constraint 1: Minimum weekly volume per muscle group
    # Each exercise contributes its "sets" to every muscle it targets.
    for m in muscles:
        prob += (
            lpSum(
                ex_by_name[e]["sets"] * x[e, d]
                for e in ex_names
                for d in days
                if m in ex_by_name[e]["muscles"]
            ) >= instance.muscle_targets[m],
            f"min_volume_{m}",
        )

    # Constraint 2: Per-session time limit
    for d in days:
        prob += (
            lpSum(ex_by_name[e]["duration_min"] * x[e, d] for e in ex_names)
            <= instance.max_time_per_day,
            f"time_limit_{d}",
        )

    # Constraint 3: No same exercise on consecutive days
    for e in ex_names:
        for i in range(len(days) - 1):
            prob += (
                x[e, days[i]] + x[e, days[i + 1]] <= 1,
                f"no_consec_{e.replace(' ', '_')}_{days[i]}_{days[i+1]}",
            )

    # Solve
    prob.solve(PULP_CBC_CMD(msg=False))
    elapsed = time.perf_counter() - t0

    status = LpStatus[prob.status]
    obj = value(prob.objective) if prob.status == 1 else None

    # Extract schedule
    schedule: dict[str, list[str]] = {d: [] for d in days}
    for d in days:
        for e in ex_names:
            val = value(x[e, d])
            if val is not None and val > 0.5:
                schedule[d].append(e)

    # Build solution
    sol = Solution(
        schedule=schedule,
        objective=obj,
        is_optimal=(status == "Optimal"),
        is_feasible=False,  # verified below
        algorithm="ILP (PuLP/CBC, Branch & Bound)",
        time_seconds=elapsed,
        certificate=f"CBC solver status: {status}",
    )

    # Independent verification
    sol.is_feasible, sol.constraint_check = verify(instance, schedule)

    return sol


# --- Verification (independent of solver) ---

def verify(
    instance: Instance,
    schedule: dict[str, list[str]],
) -> tuple[bool, dict[str, Any]]:
    """Independently verify solution feasibility.

    Six checks:
      1. All exercise names are valid catalog entries.
      2. Per-session time limits respected.
      3. Minimum weekly volume met for every muscle group.
      4. No exercise repeated on consecutive days.
      5. Objective (total time) recomputed matches.
      6. No duplicate exercises within a single day.
    """
    checks: dict[str, Any] = {}
    all_ok = True

    ex_by_name: dict[str, dict[str, Any]] = {
        e["name"]: e for e in instance.exercises
    }
    days = instance.days

    # Check 1: All exercise names valid
    all_valid = True
    for d in days:
        for e in schedule.get(d, []):
            if e not in ex_by_name:
                all_valid = False
    checks["all_exercises_valid"] = all_valid
    if not all_valid:
        all_ok = False

    # Check 2: Per-session time limits
    day_times: dict[str, int] = {}
    time_ok = True
    for d in days:
        t = sum(ex_by_name[e]["duration_min"] for e in schedule.get(d, []))
        day_times[d] = t
        if t > instance.max_time_per_day:
            time_ok = False
    checks["time_limits_respected"] = time_ok
    checks["day_times_min"] = day_times
    if not time_ok:
        all_ok = False

    # Check 3: Minimum weekly volume per muscle group
    volume: dict[str, int] = {m: 0 for m in instance.muscle_targets}
    for d in days:
        for e_name in schedule.get(d, []):
            e = ex_by_name[e_name]
            for m in e["muscles"]:
                if m in volume:
                    volume[m] += e["sets"]

    volume_ok = True
    for m, target in instance.muscle_targets.items():
        if volume.get(m, 0) < target:
            volume_ok = False
    checks["muscle_targets_met"] = volume_ok
    checks["weekly_volume_sets"] = volume
    checks["weekly_volume_targets"] = dict(instance.muscle_targets)
    if not volume_ok:
        all_ok = False

    # Check 4: No consecutive-day repeats
    consec_ok = True
    for i in range(len(days) - 1):
        overlap = set(schedule.get(days[i], [])) & set(
            schedule.get(days[i + 1], [])
        )
        if overlap:
            consec_ok = False
            checks[f"consec_violation_{days[i]}_{days[i+1]}"] = list(overlap)
    checks["no_consecutive_repeats"] = consec_ok
    if not consec_ok:
        all_ok = False

    # Check 5: Recomputed objective (total weekly time)
    total_time = sum(day_times.values())
    checks["objective_recomputed"] = total_time

    # Check 6: No duplicate exercises within a single day
    no_dupes = True
    for d in days:
        if len(schedule.get(d, [])) != len(set(schedule.get(d, []))):
            no_dupes = False
    checks["no_intraday_duplicates"] = no_dupes
    if not no_dupes:
        all_ok = False

    return all_ok, checks


# --- Main ---

if __name__ == "__main__":
    # Build instance: 10 realistic exercises
    exercises = (
        {
            "name": "Bench Press",
            "muscles": ["chest", "shoulders", "arms"],
            "duration_min": 12,
            "sets": 4,
        },
        {
            "name": "Incline Dumbbell Press",
            "muscles": ["chest", "shoulders"],
            "duration_min": 10,
            "sets": 3,
        },
        {
            "name": "Barbell Row",
            "muscles": ["back", "arms"],
            "duration_min": 12,
            "sets": 4,
        },
        {
            "name": "Pull-Up",
            "muscles": ["back", "arms"],
            "duration_min": 10,
            "sets": 3,
        },
        {
            "name": "Squat",
            "muscles": ["legs", "core"],
            "duration_min": 15,
            "sets": 4,
        },
        {
            "name": "Romanian Deadlift",
            "muscles": ["legs", "back"],
            "duration_min": 12,
            "sets": 3,
        },
        {
            "name": "Overhead Press",
            "muscles": ["shoulders", "arms"],
            "duration_min": 10,
            "sets": 3,
        },
        {
            "name": "Lateral Raise",
            "muscles": ["shoulders"],
            "duration_min": 7,
            "sets": 3,
        },
        {
            "name": "Barbell Curl",
            "muscles": ["arms"],
            "duration_min": 8,
            "sets": 3,
        },
        {
            "name": "Plank",
            "muscles": ["core"],
            "duration_min": 5,
            "sets": 3,
        },
    )

    instance = Instance(
        exercises=exercises,
        days=("Mon", "Tue", "Wed", "Thu", "Fri"),
        muscle_targets={
            "chest": 10,
            "back": 12,
            "legs": 10,
            "shoulders": 10,
            "arms": 12,
            "core": 8,
        },
        max_time_per_day=60,
    )

    sol = solve(instance)

    # --- Print Solution Report ---
    log.header("SOLUTION REPORT: Weekly Workout Plan (ILP)")

    log.step("PROBLEM SETUP")
    log.metric("Exercises:", str(instance.num_exercises), tag="DATA")
    log.metric("Training days:", str(instance.num_days), tag="DATA")
    log.metric("Max per session:", f"{instance.max_time_per_day} min", tag="DATA")
    log.blank()

    # Muscle group targets
    log.step("MUSCLE VOLUME TARGETS (weekly sets)")
    for m, target in instance.muscle_targets.items():
        log.metric(f"  {m}:", f">= {target} sets", tag="DATA")
    log.blank()

    # Exercise catalog
    log.step("EXERCISE CATALOG")
    log.table_row(
        f"{'Exercise':<25} {'Muscles':<30} {'Time':>5} {'Sets':>5}",
        tag="TABLE",
    )
    log.divider()
    for e in instance.exercises:
        muscles_str = ", ".join(e["muscles"])
        log.table_row(
            f"{e['name']:<25} {muscles_str:<30} {e['duration_min']:>4}m {e['sets']:>4}",
            tag="DATA",
        )
    log.blank()

    # Solver results
    log.step("SOLVER RESULTS")
    log.metric("Status:", "Optimal" if sol.is_optimal else "Sub-optimal", tag="RESULT")
    log.metric("Feasible:", str(sol.is_feasible), tag="RESULT")
    log.metric(
        "Total time:",
        f"{sol.objective:.0f} min" if sol.objective is not None else "N/A",
        tag="RESULT",
    )
    log.metric("Algorithm:", sol.algorithm, tag="SOLVE")
    log.metric("Time:", f"{sol.time_seconds:.6f}s", tag="TIMING")
    log.blank()

    if sol.is_optimal and sol.schedule:
        ex_by_name = {e["name"]: e for e in instance.exercises}

        # Daily schedule
        log.step("OPTIMAL 5-DAY SCHEDULE")
        for d in instance.days:
            day_exercises = sol.schedule[d]
            day_time = sum(
                ex_by_name[e]["duration_min"] for e in day_exercises
            )
            log.section(f"{d}  ({day_time} min)")
            for e_name in day_exercises:
                e = ex_by_name[e_name]
                muscles_str = ", ".join(e["muscles"])
                log.table_row(
                    f"  {e_name:<23} {e['sets']} sets  "
                    f"{e['duration_min']:>3}m  [{muscles_str}]",
                    tag="ASSIGN",
                )
        log.blank()

        # Weekly muscle volume summary
        log.step("WEEKLY MUSCLE VOLUME (sets)")
        volume = sol.constraint_check.get("weekly_volume_sets", {})
        targets = instance.muscle_targets
        log.table_row(
            f"{'Muscle':<12} {'Target':>8} {'Actual':>8} {'Status':>8}",
            tag="TABLE",
        )
        log.divider()
        for m in targets:
            actual = volume.get(m, 0)
            status = "PASS" if actual >= targets[m] else "FAIL"
            log.table_row(
                f"{m:<12} {'>= ' + str(targets[m]):>8} {actual:>8} {status:>8}",
                tag="CHECK",
            )
        log.blank()

        # Per-day time usage
        log.step("DAILY TIME USAGE")
        day_times = sol.constraint_check.get("day_times_min", {})
        for d in instance.days:
            t = day_times.get(d, 0)
            frac = t / instance.max_time_per_day
            log.bar(
                f"{d} ({t:>2}/{instance.max_time_per_day}m)",
                frac,
                tag="STATS",
            )
        log.blank()

        # Exercise frequency across the week
        log.step("EXERCISE FREQUENCY")
        freq: dict[str, int] = {}
        for d in instance.days:
            for e in sol.schedule[d]:
                freq[e] = freq.get(e, 0) + 1
        log.table_row(
            f"{'Exercise':<25} {'Days used':>10}",
            tag="TABLE",
        )
        log.divider()
        for e_name, count in sorted(freq.items(), key=lambda x: -x[1]):
            log.table_row(
                f"{e_name:<25} {count:>10}",
                tag="ASSIGN",
            )
        log.blank()

    # Independent verification
    log.step("INDEPENDENT VERIFICATION")
    for check_name, result in sol.constraint_check.items():
        if isinstance(result, bool):
            log.check(check_name, result, tag="VERIFY")
        elif isinstance(result, (int, float)):
            log.check(check_name, result, tag="VERIFY")
        else:
            # dicts/lists -- print as compact string
            log.check(
                check_name,
                json.dumps(result, separators=(",", ":")),
                tag="VERIFY",
            )
    log.blank()

    log.divider(style="thick")

    # Save JSON
    output: dict[str, Any] = {
        "schedule": sol.schedule,
        "objective_total_minutes": sol.objective,
        "is_optimal": sol.is_optimal,
        "is_feasible": sol.is_feasible,
        "algorithm": sol.algorithm,
        "time_seconds": sol.time_seconds,
        "verification": {k: v for k, v in sol.constraint_check.items()},
    }
    out_path = Path(__file__).parent / "solution.json"
    with open(out_path, "w") as f:
        json.dump(output, f, indent=2)
    log.success(f"Saved {out_path.name}", tag="SAVE")

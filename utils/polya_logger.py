#!/usr/bin/env python3
"""Crawl4ai-style colorful logger for uber-polya solvers.

Provides structured, color-coded terminal output with semantic tags,
Unicode icons, and box-drawing characters for headers.

Usage:
    from utils.polya_logger import PolyaLogger
    log = PolyaLogger()

    log.header("My Solver Report")
    log.info("Computing solution...", tag="SOLVE")
    log.success("Optimal found", tag="COMPLETE", params={"obj": 42})
    log.check("feasibility", True)
    log.bar("n=25", 0.85, tag="POWER", marker=" <-- current")
"""
from __future__ import annotations

import sys


# ── ANSI escape codes ───────────────────────────────────────────────

class _C:
    """ANSI color constants."""
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"

    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"

    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"


# ── Log levels ──────────────────────────────────────────────────────

DEBUG   = 0
INFO    = 1
SUCCESS = 2
WARNING = 3
ERROR   = 4

_LEVEL_COLORS = {
    DEBUG:   _C.BRIGHT_BLACK,
    INFO:    _C.CYAN,
    SUCCESS: _C.GREEN,
    WARNING: _C.YELLOW,
    ERROR:   _C.RED,
}

_LEVEL_TAGS = {
    DEBUG:   "DEBUG",
    INFO:    "INFO",
    SUCCESS: "SUCCESS",
    WARNING: "WARNING",
    ERROR:   "ERROR",
}


# ── Semantic tag icons ──────────────────────────────────────────────

ICONS: dict[str, str] = {
    # Pipeline phases
    "INIT":        "\u2192",    # →
    "MODEL":       "\u25c6",    # ◆
    "SOLVE":       "\u2699",    # ⚙
    "VERIFY":      "\u2713",    # ✓
    "INTERPRET":   "\u25c8",    # ◈
    "COMPLETE":    "\u25cf",    # ●

    # Computation domains
    "STATS":       "\u25aa",    # ▪
    "HYPOTHESIS":  "\u2295",    # ⊕
    "BAYESIAN":    "\u223f",    # ∿
    "POWER":       "\u26a1",    # ⚡
    "SENSITIVITY": "\u25c7",    # ◇
    "FRONTIER":    "\u2248",    # ≈
    "PROOF":       "\u220e",    # ∎

    # I/O and results
    "DATA":        "\u25b8",    # ▸
    "RESULT":      "\u2605",    # ★
    "SAVE":        "\u2193",    # ↓
    "VIZ":         "\u25a3",    # ▣
    "TABLE":       "\u2261",    # ≡

    # Actions
    "RECOMMEND":   "\u25ba",    # ►
    "TEST":        "\u2299",    # ⊙
    "CHECK":       "\u25c9",    # ◉
    "ASSIGN":      "\u229e",    # ⊞
    "OPTIMIZE":    "\u25b2",    # ▲

    # Standard log levels
    "INFO":        "\u2139",    # ℹ
    "SUCCESS":     "\u2714",    # ✔
    "WARNING":     "\u26a0",    # ⚠
    "ERROR":       "\u00d7",    # ×
    "DEBUG":       "\u22ef",    # ⋯
    "TIMING":      "\u23f1",    # ⏱
}


# ── Box-drawing characters ─────────────────────────────────────────

_H  = "\u2500"  # ─
_V  = "\u2502"  # │
_TL = "\u250c"  # ┌
_TR = "\u2510"  # ┐
_BL = "\u2514"  # └
_BR = "\u2518"  # ┘

_DH  = "\u2550"  # ═
_DV  = "\u2551"  # ║
_DTL = "\u2554"  # ╔
_DTR = "\u2557"  # ╗
_DBL = "\u255a"  # ╚
_DBR = "\u255d"  # ╝


# ── Logger ──────────────────────────────────────────────────────────

class PolyaLogger:
    """Crawl4ai-style colorful logger with semantic tags.

    Every log line follows the pattern:
        [TAG]····· ◆ message | param1: val1 | param2: val2

    Tags are fixed-width and dot-padded for visual alignment.
    Each tag has its own Unicode icon. Lines are colored by log level.
    """

    def __init__(self, verbose: bool = True, tag_width: int = 14,
                 use_color: bool = True) -> None:
        self.verbose = verbose
        self.tag_width = tag_width
        self.use_color = use_color

    # ── Internal helpers ──

    def _c(self, text: str, color: str) -> str:
        """Wrap text in ANSI color codes."""
        if not self.use_color:
            return text
        return f"{color}{text}{_C.RESET}"

    def _fmt_tag(self, tag: str) -> str:
        """Format a tag with fixed-width dot-padding: [TAG]·····"""
        inner = f"[{tag}]"
        pad = max(0, self.tag_width - len(inner))
        return inner + "\u00b7" * pad  # middle dot ·

    def _icon(self, tag: str) -> str:
        """Get the Unicode icon for a tag."""
        return ICONS.get(tag, "\u2022")  # default: bullet •

    def _log(self, level: int, message: str, tag: str = "",
             params: dict | None = None) -> None:
        """Core log method. Formats and prints a single tagged line."""
        if not self.verbose:
            return

        if not tag:
            tag = _LEVEL_TAGS.get(level, "INFO")

        color = _LEVEL_COLORS.get(level, _C.CYAN)
        line = f"{self._fmt_tag(tag)} {self._icon(tag)} {message}"

        if params:
            parts = [f"{k}: {v}" for k, v in params.items()]
            line += " | " + " | ".join(parts)

        print(self._c(line, color))

    # ── Level methods ──

    def info(self, message: str, tag: str = "INFO", **kwargs) -> None:
        self._log(INFO, message, tag, **kwargs)

    def success(self, message: str, tag: str = "SUCCESS", **kwargs) -> None:
        self._log(SUCCESS, message, tag, **kwargs)

    def warning(self, message: str, tag: str = "WARNING", **kwargs) -> None:
        self._log(WARNING, message, tag, **kwargs)

    def error(self, message: str, tag: str = "ERROR", **kwargs) -> None:
        self._log(ERROR, message, tag, **kwargs)

    def debug(self, message: str, tag: str = "DEBUG", **kwargs) -> None:
        self._log(DEBUG, message, tag, **kwargs)

    # ── Structured output ──

    def header(self, title: str, width: int = 70, style: str = "double") -> None:
        """Print a boxed header using box-drawing characters.

        double style:  ╔══════════════════════╗
                       ║   Title Goes Here    ║
                       ╚══════════════════════╝

        single style:  ┌──────────────────────┐
                       │   Title Goes Here    │
                       └──────────────────────┘
        """
        if not self.verbose:
            return

        iw = width - 2  # inner width (minus two border chars)

        if style == "double":
            h, v, tl, tr, bl, br = _DH, _DV, _DTL, _DTR, _DBL, _DBR
            border_color = _C.BRIGHT_CYAN
            text_color = f"{_C.BRIGHT_WHITE}{_C.BOLD}"
        else:
            h, v, tl, tr, bl, br = _H, _V, _TL, _TR, _BL, _BR
            border_color = _C.CYAN
            text_color = f"{_C.WHITE}{_C.BOLD}"

        top = f"{tl}{h * iw}{tr}"
        mid = f"{v} {title:^{iw - 2}} {v}"
        bot = f"{bl}{h * iw}{br}"

        print()
        print(self._c(top, border_color))
        print(self._c(mid, text_color))
        print(self._c(bot, border_color))
        print()

    def section(self, title: str, width: int = 68) -> None:
        """Print a section header with a colored underline.

          PHASE 3: EXECUTE
          ════════════════════════════════════════════════════
        """
        if not self.verbose:
            return
        print()
        print(self._c(f"  {title}", f"{_C.BRIGHT_WHITE}{_C.BOLD}"))
        print(self._c(f"  {_DH * width}", _C.BRIGHT_CYAN))

    def step(self, title: str, width: int = 68) -> None:
        """Print a step sub-header with a thin underline.

          STEP 1: Descriptive Statistics
          ──────────────────────────────────────────────────
        """
        if not self.verbose:
            return
        print()
        print(self._c(f"  {title}", f"{_C.CYAN}{_C.BOLD}"))
        print(self._c(f"  {_H * width}", _C.BRIGHT_BLACK))

    def metric(self, label: str, value: str, tag: str = "STATS",
               level: int = INFO, pad: int = 18) -> None:
        """Print a key-value metric as a tagged line.

        [STATS]······· ▪ t-statistic:      3.456
        """
        if not self.verbose:
            return
        color = _LEVEL_COLORS.get(level, _C.CYAN)
        formatted = f"{self._fmt_tag(tag)} {self._icon(tag)} {label:<{pad}} {value}"
        print(self._c(formatted, color))

    def check(self, name: str, passed: bool | str | int | float,
              tag: str = "CHECK") -> None:
        """Print a verification check result.

        [CHECK]······· ◉ feasibility_ok                     PASS ✔
        [CHECK]······· ◉ objective_value                    85.0
        """
        if not self.verbose:
            return

        fmt_tag = self._c(f"{self._fmt_tag(tag)} {self._icon(tag)} ", _C.CYAN)

        # Convert numpy scalars to Python types (avoids isinstance issues)
        if hasattr(passed, 'item'):
            passed = passed.item()

        if isinstance(passed, bool):
            if passed:
                status = self._c("PASS \u2714", _C.GREEN)
            else:
                status = self._c("FAIL \u00d7", _C.RED)
        else:
            status = self._c(str(passed), _C.YELLOW)

        print(f"{fmt_tag}{name:<38} {status}")

    def bar(self, label: str, value: float, max_width: int = 30,
            tag: str = "POWER", marker: str = "") -> None:
        """Print a horizontal bar chart line.

        [POWER]······· ⚡ n= 25: 85% ████████████████████████░░░░░░ <-- current
        """
        if not self.verbose:
            return
        filled = int(value * max_width)
        bar_str = "\u2588" * filled + "\u2591" * (max_width - filled)
        color = _LEVEL_COLORS.get(INFO, _C.CYAN)
        line = f"{self._fmt_tag(tag)} {self._icon(tag)} {label} {bar_str} {value:.0%}{marker}"
        print(self._c(line, color))

    def table_row(self, formatted_line: str, tag: str = "TABLE",
                  level: int = INFO) -> None:
        """Print a pre-formatted table row with tag prefix.

        [TABLE]······· ≡ Jazz        25    19.2     2.8    19.1     4.0
        """
        if not self.verbose:
            return
        color = _LEVEL_COLORS.get(level, _C.CYAN)
        line = f"{self._fmt_tag(tag)} {self._icon(tag)} {formatted_line}"
        print(self._c(line, color))

    def divider(self, width: int = 70, style: str = "thin") -> None:
        """Print a visual divider line."""
        if not self.verbose:
            return
        char = _DH if style == "thick" else _H
        color = _C.BRIGHT_BLACK if style == "thin" else _C.BRIGHT_CYAN
        print(self._c(char * width, color))

    def blank(self) -> None:
        """Print a blank line (respects verbose)."""
        if self.verbose:
            print()

    def text(self, message: str, indent: int = 2,
             color: str = "", bold: bool = False) -> None:
        """Print plain text with optional indent/color (for multi-line prose)."""
        if not self.verbose:
            return
        prefix = " " * indent
        if color or bold:
            c = color or _C.WHITE
            if bold:
                c = f"{c}{_C.BOLD}"
            print(self._c(f"{prefix}{message}", c))
        else:
            print(f"{prefix}{message}")

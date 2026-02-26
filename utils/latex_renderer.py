#!/usr/bin/env python3
"""LaTeX/PDF report renderer for the uber-polya pipeline.

Accepts structured artifacts from the three pipeline phases, renders
Jinja2 templates into a ``.tex`` document, and compiles a ``.pdf``
using fpdf2 + matplotlib (no system LaTeX installation required).

Usage::

    from utils.latex_data import (
        FormalModel, SolutionReport, InterpretationReport, ReportConfig,
    )
    from utils.latex_renderer import LatexRenderer

    config = ReportConfig(title="My Report", output_dir=Path("output"))
    renderer = LatexRenderer(config)
    renderer.render_tex(model, solution, interpretation)
    renderer.render_pdf(model, solution, interpretation)
"""
from __future__ import annotations

import datetime
import io
import logging
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import jinja2

# Suppress harmless fpdf2 font-subsetting warnings about newline glyphs
logging.getLogger("fpdf2").setLevel(logging.ERROR)

from utils.latex_data import (
    Constraint,
    Figure,
    FormalModel,
    InterpretationReport,
    MappingRow,
    ReportConfig,
    SensitivityRow,
    SolutionReport,
    Variable,
    VerificationCheck,
)

# ── Paths ─────────────────────────────────────────────────────────────

_PACKAGE_ROOT = Path(__file__).resolve().parent.parent
_TEMPLATES_DIR = _PACKAGE_ROOT / "templates" / "latex"


# ── LaTeX escaping ────────────────────────────────────────────────────

_LATEX_SPECIAL = re.compile(r"([&%$#_{}~^\\])")
_LATEX_REPLACE = {
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
    "\\": r"\textbackslash{}",
}


def _escape_latex(text: Any) -> str:
    """Escape LaTeX special characters in *text*."""
    s = str(text)
    return _LATEX_SPECIAL.sub(lambda m: _LATEX_REPLACE[m.group(1)], s)


# ── Jinja2 environment ───────────────────────────────────────────────

def _make_jinja_env() -> jinja2.Environment:
    """Create a Jinja2 environment with LaTeX-safe delimiters."""
    env = jinja2.Environment(
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        line_comment_prefix="%#",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(str(_TEMPLATES_DIR)),
        undefined=jinja2.StrictUndefined,
    )
    env.filters["e"] = _escape_latex
    return env


# ── Math rendering via matplotlib ─────────────────────────────────────

def _render_math_to_png(latex_expr: str, dpi: int = 150) -> bytes:
    """Render a LaTeX math expression to PNG bytes via matplotlib.

    Uses matplotlib's built-in mathtext renderer — no system LaTeX needed.
    """
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig = plt.figure(figsize=(0.01, 0.01))
    fig.text(
        0.5, 0.5,
        f"${latex_expr}$",
        fontsize=14,
        ha="center", va="center",
    )
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight", pad_inches=0.05,
                transparent=True)
    plt.close(fig)
    buf.seek(0)
    return buf.read()


# ── PDF builder using fpdf2 ──────────────────────────────────────────

class _PdfBuilder:
    """Build a structured PDF report using fpdf2 + matplotlib math."""

    # Page geometry
    _MARGIN = 20
    _PAGE_W = 210  # A4 mm
    _CONTENT_W = 210 - 2 * 20  # 170 mm

    # DejaVu Sans paths (widely available on Linux; macOS/Windows fallbacks below)
    _FONT_PATHS = {
        "": "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "B": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "I": "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
        "BI": "/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf",
    }
    _MONO_PATHS = {
        "": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "B": "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    }

    def __init__(self, config: ReportConfig) -> None:
        from fpdf import FPDF

        self.pdf = FPDF()
        self.pdf.set_auto_page_break(auto=True, margin=25)
        self.config = config
        self._tmp = Path(tempfile.mkdtemp(prefix="polya_math_"))
        self._has_unicode = self._register_fonts()

    def _register_fonts(self) -> bool:
        """Register DejaVu Sans (Unicode) if available. Returns True on success."""
        try:
            for style, path in self._FONT_PATHS.items():
                if Path(path).exists():
                    self.pdf.add_font("DejaVu", style=style, fname=path)
            for style, path in self._MONO_PATHS.items():
                if Path(path).exists():
                    self.pdf.add_font("DejaVuMono", style=style, fname=path)
            return True
        except Exception:
            return False

    # ── helpers ───────────────────────────────────────────────────────

    def _add_page(self) -> None:
        self.pdf.add_page()
        self.pdf.set_margins(self._MARGIN, self._MARGIN, self._MARGIN)

    def _set_font(self, style: str = "", size: int = 11) -> None:
        family = "DejaVu" if self._has_unicode else "Helvetica"
        self.pdf.set_font(family, style=style, size=size)

    def _set_mono_font(self, style: str = "", size: int = 8) -> None:
        family = "DejaVuMono" if self._has_unicode else "Courier"
        self.pdf.set_font(family, style=style, size=size)

    @staticmethod
    def _clean(text: str) -> str:
        """Strip newlines/carriage returns — for cell() which can't handle them."""
        return str(text).replace("\n", " ").replace("\r", "")

    @staticmethod
    def _latex_to_unicode(text: str) -> str:
        """Convert common LaTeX math symbols to Unicode for table cells."""
        s = str(text)
        # Greek letters
        greek = {
            r"\alpha": "\u03b1", r"\beta": "\u03b2", r"\gamma": "\u03b3",
            r"\delta": "\u03b4", r"\epsilon": "\u03b5", r"\zeta": "\u03b6",
            r"\eta": "\u03b7", r"\theta": "\u03b8", r"\lambda": "\u03bb",
            r"\mu": "\u03bc", r"\nu": "\u03bd", r"\pi": "\u03c0",
            r"\rho": "\u03c1", r"\sigma": "\u03c3", r"\tau": "\u03c4",
            r"\phi": "\u03c6", r"\chi": "\u03c7", r"\psi": "\u03c8",
            r"\omega": "\u03c9", r"\Delta": "\u0394", r"\Sigma": "\u03a3",
        }
        for cmd, char in greek.items():
            s = s.replace(cmd, char)
        # Math symbols
        symbols = {
            r"\mathbb{{R}}": "\u211d", r"\mathbb{R}": "\u211d",
            r"\mathbb{{Z}}": "\u2124", r"\mathbb{Z}": "\u2124",
            r"\mathbb{{N}}": "\u2115", r"\mathbb{N}": "\u2115",
            r"\ge": "\u2265", r"\le": "\u2264", r"\ne": "\u2260",
            r"\in": "\u2208", r"\notin": "\u2209",
            r"\forall": "\u2200", r"\exists": "\u2203",
            r"\infty": "\u221e", r"\times": "\u00d7",
            r"\pm": "\u00b1", r"\cdot": "\u00b7",
            r"\rightarrow": "\u2192", r"\leftarrow": "\u2190",
            r"\subset": "\u2282", r"\cup": "\u222a", r"\cap": "\u2229",
        }
        for cmd, char in symbols.items():
            s = s.replace(cmd, char)
        # Subscript/superscript patterns
        s = re.sub(r"_\{([^}]+)\}", r"_\1", s)  # _{ij} -> _ij
        s = re.sub(r"\^\{([^}]+)\}", r"^\1", s)  # ^{+} -> ^+
        s = re.sub(r"_\{?\{?>0\}?\}", r"₊", s)   # _{{>0}} -> ₊
        s = re.sub(r"_\{\s*\\ge\s*0\s*\}", r"₊", s)
        # Clean remaining braces and backslashes
        s = s.replace(r"\{", "{").replace(r"\}", "}")
        s = s.replace(r"\,", " ").replace(r"\;", " ").replace(r"\quad", "  ")
        s = s.replace(r"\bar", "x\u0305")  # x-bar approximation
        s = s.replace(r"\hat", "x\u0302")  # x-hat approximation
        return s.replace("\n", " ").replace("\r", "")

    def _heading(self, text: str, level: int = 1) -> None:
        sizes = {1: 18, 2: 14, 3: 12}
        self._set_font("B", sizes.get(level, 11))
        self.pdf.ln(4)
        self.pdf.cell(w=0, h=10, text=self._clean(text), new_x="LMARGIN", new_y="NEXT")
        if level == 1:
            self.pdf.set_draw_color(30, 64, 175)  # polyablue
            self.pdf.line(
                self._MARGIN, self.pdf.get_y(),
                self._PAGE_W - self._MARGIN, self.pdf.get_y(),
            )
            self.pdf.ln(3)
        self.pdf.ln(2)

    def _body(self, text: str) -> None:
        self._set_font(size=11)
        self.pdf.multi_cell(w=0, h=6, text=text)
        self.pdf.ln(2)

    def _bold_line(self, label: str, value: str) -> None:
        self._set_font("B", 11)
        self.pdf.cell(w=45, h=7, text=f"{label}:")
        self._set_font(size=11)
        self.pdf.cell(w=0, h=7, text=self._clean(value), new_x="LMARGIN", new_y="NEXT")

    def _math_image(self, expr: str, centered: bool = True,
                    max_w: int = 100) -> None:
        """Render a LaTeX expression and embed as image at natural size."""
        import struct

        safe = re.sub(r"[^a-zA-Z0-9]", "_", expr)[:60]
        path = self._tmp / f"eq_{safe}.png"
        if not path.exists():
            try:
                path.write_bytes(_render_math_to_png(expr, dpi=150))
            except Exception:
                # Fallback: render as plain text if matplotlib can't parse it
                self._body(expr)
                return

        # Read the natural pixel width from the PNG header to size correctly
        try:
            with open(str(path), "rb") as f:
                f.seek(16)
                width_px = struct.unpack(">I", f.read(4))[0]
            # Convert pixels to mm at rendering DPI (150)
            natural_w = width_px / 150 * 25.4
        except Exception:
            natural_w = max_w

        w = min(natural_w, max_w, self._CONTENT_W)
        self.pdf.ln(2)
        if centered:
            x = (self._PAGE_W - w) / 2
            self.pdf.image(str(path), x=x, w=w)
        else:
            self.pdf.image(str(path), w=w)
        self.pdf.ln(4)

    def _try_math_inline(self, expr: str) -> bool:
        """Try to render expr as inline math. Returns True if it contained LaTeX."""
        if any(c in expr for c in ("\\", "_{", "^{", r"\sum", r"\max", r"\min",
                                     r"\le", r"\ge", r"\in", r"\forall",
                                     r"\frac", r"\text")):
            self._math_image(expr, centered=True, max_w=100)
            return True
        return False

    def _bullet(self) -> str:
        return "\u2022" if self._has_unicode else "-"

    def _check(self, name: str, passed: bool, detail: str) -> None:
        mark = ("\u2713" if self._has_unicode else "[OK]") if passed else ("\u2717" if self._has_unicode else "[X]")
        r, g, b = (21, 128, 61) if passed else (185, 28, 28)
        self._set_font("B", 11)
        self.pdf.set_text_color(r, g, b)
        self.pdf.cell(w=8, h=7, text=mark)
        self.pdf.set_text_color(0, 0, 0)
        self._set_font(size=11)
        self.pdf.cell(w=55, h=7, text=self._clean(name))
        self.pdf.cell(w=0, h=7, text=self._clean(detail), new_x="LMARGIN", new_y="NEXT")

    # ── title page ────────────────────────────────────────────────────

    def _title_page(self) -> None:
        self._add_page()
        self.pdf.ln(50)
        self._set_font("B", 26)
        self.pdf.cell(w=0, h=15, text=self.config.title, align="C",
                      new_x="LMARGIN", new_y="NEXT")
        self.pdf.ln(8)
        self._set_font(size=12)
        self.pdf.set_text_color(75, 85, 99)  # polyagray
        self.pdf.cell(w=0, h=8, text=f"Generated by {self.config.author}",
                      align="C", new_x="LMARGIN", new_y="NEXT")
        date = self.config.date or datetime.date.today().isoformat()
        self.pdf.cell(w=0, h=8, text=date, align="C",
                      new_x="LMARGIN", new_y="NEXT")
        self.pdf.cell(w=0, h=8, text=f"Mode: {self.config.pipeline_mode}",
                      align="C", new_x="LMARGIN", new_y="NEXT")
        self.pdf.set_text_color(0, 0, 0)

    # ── section builders ──────────────────────────────────────────────

    def _section_model(self, model: FormalModel) -> None:
        self._add_page()
        self._heading("1. Problem Formulation")

        self._bold_line("Problem Type", model.problem_type)
        self._bold_line("Domain", model.domain)
        if model.named_problem:
            self._bold_line("Named Problem", model.named_problem)
        self.pdf.ln(3)

        # Universe
        self._heading("Universe", 2)
        for s in model.universe:
            self._set_font(size=11)
            self.pdf.cell(w=6, h=7, text=self._bullet())
            self.pdf.cell(w=0, h=7, text=self._clean(s), new_x="LMARGIN", new_y="NEXT")

        # Variables table
        self._heading("Variables", 2)
        self._set_font("B", 10)
        col_w = [35, 75, 60]
        headers = ["Symbol", "Meaning", "Type / Range"]
        for i, h in enumerate(headers):
            self.pdf.cell(w=col_w[i], h=7, text=h, border="B")
        self.pdf.ln()
        self._set_font(size=10)
        for v in model.variables:
            self.pdf.cell(w=col_w[0], h=7, text=self._latex_to_unicode(v.name))
            self.pdf.cell(w=col_w[1], h=7, text=self._clean(v.meaning))
            self.pdf.cell(w=col_w[2], h=7, text=self._latex_to_unicode(v.type_range),
                          new_x="LMARGIN", new_y="NEXT")

        # Structure
        self._heading("Structure", 2)
        self._body(model.structure)

        # Mapping table
        self._heading("Real-World Mapping", 2)
        self._set_font("B", 10)
        col_w = [85, 85]
        for i, h in enumerate(["Real-World Concept", "Mathematical Object"]):
            self.pdf.cell(w=col_w[i], h=7, text=h, border="B")
        self.pdf.ln()
        self._set_font(size=10)
        for row in model.mapping:
            self.pdf.cell(w=col_w[0], h=7, text=self._clean(row.real_world))
            self.pdf.cell(w=col_w[1], h=7, text=self._latex_to_unicode(row.math_object),
                          new_x="LMARGIN", new_y="NEXT")

        # Constraints
        self._heading("Constraints", 2)
        for c in model.constraints:
            self._set_font("B", 11)
            self.pdf.cell(w=12, h=7, text=f"({c.number})")
            # Try rendering the constraint as a math equation
            if not self._try_math_inline(c.formal):
                # Plain text fallback
                self._set_font(size=11)
                self.pdf.cell(w=100, h=7, text=self._clean(c.formal))
            self.pdf.set_text_color(75, 85, 99)
            self._set_font("I", 10)
            self.pdf.cell(w=0, h=6, text=self._clean(c.origin),
                          new_x="LMARGIN", new_y="NEXT")
            self.pdf.set_text_color(0, 0, 0)
            self.pdf.ln(1)

        # Objective / Claim
        if model.objective:
            self._heading("Objective", 2)
            self._math_image(model.objective)
        if model.claim:
            self._heading("Claim", 2)
            self._math_image(model.claim)

        # Approach
        self._heading("Approach", 2)
        self._bold_line("Suggested approach", model.suggested_approach)
        self._bold_line("Complexity class", model.complexity_class)
        if model.available_tools:
            self._bold_line("Available tools", ", ".join(model.available_tools))

    def _section_solve(self, solution: SolutionReport) -> None:
        self._add_page()
        self._heading("2. Solution")

        self._bold_line("Answer", solution.answer)
        if solution.objective_value is not None:
            self._bold_line("Objective Value", str(solution.objective_value))
        self._bold_line("Optimal", "Yes" if solution.is_optimal else "No / Unknown")
        self._bold_line("Feasible", "Yes" if solution.is_feasible else "No")
        self._bold_line("Algorithm", f"{solution.algorithm}  {solution.complexity}")
        self._bold_line("Time", f"{solution.time_seconds:.4f}s")
        if solution.certificate:
            self._bold_line("Certificate", solution.certificate)
        self.pdf.ln(3)

        # Details
        self._heading("Solution Details", 2)
        self._body(solution.details)

        # Verification
        self._heading("Verification", 2)
        if solution.verification:
            for ck in solution.verification:
                self._check(ck.name, ck.passed, ck.value)
        else:
            self._body("No independent verification checks recorded.")

    def _section_interpret(self, interp: InterpretationReport) -> None:
        self._add_page()
        self._heading("3. Interpretation")

        self._heading("The Question", 2)
        self._body(interp.question)

        self._heading("The Answer", 2)
        # Highlight box
        self.pdf.set_fill_color(254, 243, 199)  # polyawarn
        self._set_font("B", 12)
        answer_clean = interp.answer.replace("\n", " ").replace("\r", "")
        self.pdf.multi_cell(w=0, h=8, text=answer_clean, fill=True)
        self.pdf.ln(4)

        self._heading("What This Means", 2)
        self._body(interp.what_this_means)

        # Sensitivity table
        if interp.sensitivity:
            self._heading("Sensitivity Analysis", 2)
            self._set_font("B", 10)
            col_w = [35, 25, 25, 30, 25]
            headers = ["Parameter", "Current", "Change", "New Obj.", "Class"]
            for i, h in enumerate(headers):
                self.pdf.cell(w=col_w[i], h=7, text=h, border="B")
            self.pdf.ln()
            self._set_font(size=10)
            color_map = {
                "robust": (21, 128, 61),
                "sensitive": (75, 85, 99),
                "critical": (185, 28, 28),
            }
            for row in interp.sensitivity:
                self.pdf.cell(w=col_w[0], h=7, text=self._clean(row.parameter))
                self.pdf.cell(w=col_w[1], h=7, text=self._clean(row.current))
                self.pdf.cell(w=col_w[2], h=7, text=self._clean(row.change))
                self.pdf.cell(w=col_w[3], h=7, text=self._clean(row.new_objective))
                r, g, b = color_map.get(row.classification, (0, 0, 0))
                self.pdf.set_text_color(r, g, b)
                self.pdf.cell(w=col_w[4], h=7, text=self._clean(row.classification),
                              new_x="LMARGIN", new_y="NEXT")
                self.pdf.set_text_color(0, 0, 0)

        # Figures
        if interp.figures:
            self._heading("Visualizations", 2)
            for fig in interp.figures:
                if fig.path.exists():
                    self.pdf.image(str(fig.path), w=self._CONTENT_W)
                    self._set_font("I", 10)
                    self.pdf.cell(w=0, h=7, text=self._clean(fig.caption), align="C",
                                  new_x="LMARGIN", new_y="NEXT")
                    self.pdf.ln(4)

        # Recommendations
        if interp.recommendations:
            self._heading("Recommendations", 2)
            for i, rec in enumerate(interp.recommendations, 1):
                self._set_font("B", 11)
                self.pdf.cell(w=8, h=7, text=f"{i}.")
                self._set_font(size=11)
                self.pdf.multi_cell(w=self._CONTENT_W - 8, h=7, text=rec)

        # Limitations
        if interp.limitations:
            self._heading("Limitations", 2)
            self.pdf.set_fill_color(254, 226, 226)  # polyafail
            for lim in interp.limitations:
                self._set_font(size=11)
                self.pdf.cell(w=6, h=7, text=self._bullet())
                self.pdf.multi_cell(w=self._CONTENT_W - 6, h=7, text=lim,
                                    fill=True)

    def _section_appendix(self, code: str) -> None:
        self._add_page()
        self._heading("Appendix: Solver Implementation")
        self._set_mono_font(size=7)
        for line in code.splitlines():
            self.pdf.cell(w=0, h=4, text=line, new_x="LMARGIN", new_y="NEXT")

    # ── public API ────────────────────────────────────────────────────

    def build(
        self,
        model: FormalModel | None,
        solution: SolutionReport | None,
        interpretation: InterpretationReport | None,
    ) -> bytes:
        """Build the full PDF and return bytes."""
        self._title_page()
        if model:
            self._section_model(model)
        if solution:
            self._section_solve(solution)
        if interpretation:
            self._section_interpret(interpretation)
        if self.config.include_code and solution and solution.solver_code:
            self._section_appendix(solution.solver_code)

        # Clean up temp math images
        shutil.rmtree(self._tmp, ignore_errors=True)

        # Suppress harmless font-subsetting glyph warnings from fpdf2
        import os
        import sys
        devnull = os.open(os.devnull, os.O_WRONLY)
        old_stderr = os.dup(2)
        os.dup2(devnull, 2)
        try:
            result = bytes(self.pdf.output())
        finally:
            os.dup2(old_stderr, 2)
            os.close(devnull)
            os.close(old_stderr)
        return result


# ── Main renderer class ───────────────────────────────────────────────

class LatexRenderer:
    """Render uber-polya artifacts to ``.tex`` and ``.pdf``."""

    def __init__(self, config: ReportConfig) -> None:
        self.config = config
        if config.date is None:
            config.date = datetime.date.today().isoformat()
        config.output_dir.mkdir(parents=True, exist_ok=True)

    # ── .tex via Jinja2 ──────────────────────────────────────────────

    def render_tex(
        self,
        model: FormalModel | None = None,
        solution: SolutionReport | None = None,
        interpretation: InterpretationReport | None = None,
    ) -> Path:
        """Render a complete LaTeX document from the artifacts.

        Returns the path to the generated ``.tex`` file.
        """
        env = _make_jinja_env()
        tmpl = env.get_template("report.tex.j2")

        tex_src = tmpl.render(
            config=self.config,
            model=model,
            solution=solution,
            interpretation=interpretation,
        )

        tex_path = self.config.output_dir / "report.tex"
        tex_path.write_text(tex_src, encoding="utf-8")

        # Copy polya.sty next to report.tex so pdflatex can find it
        sty_src = _TEMPLATES_DIR / "polya.sty"
        sty_dst = self.config.output_dir / "polya.sty"
        if sty_src.exists() and sty_src != sty_dst:
            shutil.copy2(sty_src, sty_dst)

        # Copy any figures referenced by the interpretation report
        if interpretation:
            for fig in interpretation.figures:
                if fig.path.exists():
                    dst = self.config.output_dir / fig.path.name
                    if fig.path != dst:
                        shutil.copy2(fig.path, dst)

        return tex_path

    # ── .pdf via fpdf2 + matplotlib ──────────────────────────────────

    def render_pdf(
        self,
        model: FormalModel | None = None,
        solution: SolutionReport | None = None,
        interpretation: InterpretationReport | None = None,
    ) -> Path:
        """Render a PDF report using fpdf2 (no system LaTeX needed).

        Returns the path to the generated ``.pdf`` file.
        """
        builder = _PdfBuilder(self.config)
        pdf_bytes = builder.build(model, solution, interpretation)

        pdf_path = self.config.output_dir / "report.pdf"
        pdf_path.write_bytes(pdf_bytes)
        return pdf_path

    # ── convenience: try pdflatex if available ────────────────────────

    def compile_tex(self) -> Path | None:
        """Try to compile report.tex with system LaTeX for higher quality.

        Returns the PDF path if successful, ``None`` otherwise.
        This is *optional* — ``render_pdf`` always works without it.
        """
        tex_path = self.config.output_dir / "report.tex"
        if not tex_path.exists():
            return None

        for compiler in ("latexmk -pdf", "pdflatex"):
            exe = compiler.split()[0]
            if shutil.which(exe) is None:
                continue
            cmd = f"{compiler} -interaction=nonstopmode -output-directory={self.config.output_dir} {tex_path}"
            try:
                subprocess.run(
                    cmd.split(),
                    cwd=str(self.config.output_dir),
                    capture_output=True,
                    timeout=60,
                )
                pdf = self.config.output_dir / "report.pdf"
                if pdf.exists():
                    return pdf
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
        return None

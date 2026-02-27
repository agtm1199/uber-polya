#!/usr/bin/env bash
# Build the First Proof submission PDF
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Step 1: Generate LaTeX ==="
python3 generate_tex.py

echo ""
echo "=== Step 2: Compile PDF (3 passes) ==="
cd output

for pass in 1 2 3; do
    echo "  Pass $pass/3..."
    pdflatex -interaction=nonstopmode firstproof.tex > /dev/null 2>&1 || {
        echo "  ERROR on pass $pass. Full log:"
        cat firstproof.log | tail -30
        exit 1
    }
done

echo ""
echo "=== Done ==="
echo "  PDF: $(pwd)/firstproof.pdf"
echo "  Pages: $(pdfinfo firstproof.pdf 2>/dev/null | grep Pages | awk '{print $2}')"
echo "  Size: $(du -h firstproof.pdf | cut -f1)"

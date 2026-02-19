#!/bin/bash
# install.sh -- Install uber-polya skills for Claude Code
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILLS_SRC="$SCRIPT_DIR/skills"

echo ""
echo "  uber-polya installer"
echo "  ===================="
echo ""
echo "  Three skills will be installed:"
echo "    /uber-model     -- Model a problem (Polya phases 1-2)"
echo "    /uber-solve     -- Solve a model   (Polya phase 3)"
echo "    /uber-interpret -- Interpret results (Polya phase 4)"
echo ""
echo "  Where would you like to install?"
echo "    1) Global:  ~/.claude/skills/  (available in all projects)"
echo "    2) Project: ./.claude/skills/  (current project only)"
echo ""
read -p "  Choice [1/2]: " choice

case "$choice" in
  1) TARGET="$HOME/.claude/skills" ;;
  2) TARGET="./.claude/skills" ;;
  *)
    echo "  Invalid choice. Exiting."
    exit 1
    ;;
esac

mkdir -p "$TARGET"

installed=0
for skill in uber-model uber-solve uber-interpret; do
  if [ -d "$TARGET/$skill" ]; then
    read -p "  $TARGET/$skill already exists. Overwrite? [y/N]: " overwrite
    if [ "$overwrite" != "y" ] && [ "$overwrite" != "Y" ]; then
      echo "  Skipped: $skill"
      continue
    fi
    rm -rf "$TARGET/$skill"
  fi
  cp -r "$SKILLS_SRC/$skill" "$TARGET/"
  echo "  Installed: $skill"
  installed=$((installed + 1))
done

echo ""
echo "  Done! $installed skill(s) installed to: $TARGET"
echo ""
echo "  Usage in Claude Code:"
echo "    /uber-model <describe your problem>"
echo "    /uber-solve"
echo "    /uber-interpret"
echo ""

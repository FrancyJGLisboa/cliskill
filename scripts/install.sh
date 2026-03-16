#!/bin/sh
# Installer for cliskill — AI-agent-friendly CLI skill framework.
# Installs /cliskill to all detected agent platforms via symlink.
# Optionally checks and installs dependencies (/clarity, /agent-skill-creator).
#
# Usage:
#   ./scripts/install.sh                # Auto-detect platforms, install
#   ./scripts/install.sh --dry-run      # Preview without changes
#   ./scripts/install.sh --uninstall    # Remove symlinks
#   ./scripts/install.sh --with-deps    # Also clone and install dependencies
#
# This script is POSIX-compatible (bash, dash, zsh, ash).

set -e

REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DRY_RUN=0
UNINSTALL=0
WITH_DEPS=0

for arg in "$@"; do
    case "$arg" in
        --dry-run)   DRY_RUN=1 ;;
        --uninstall) UNINSTALL=1 ;;
        --with-deps) WITH_DEPS=1 ;;
        --help|-h)
            echo "Usage: $0 [--dry-run] [--uninstall] [--with-deps]"
            echo ""
            echo "Installs /cliskill to all detected agent platforms."
            echo ""
            echo "Options:"
            echo "  --dry-run     Preview changes without executing"
            echo "  --uninstall   Remove cliskill symlinks"
            echo "  --with-deps   Also clone and install /clarity and /agent-skill-creator"
            exit 0
            ;;
    esac
done

# --- Platform detection ---

detect_platforms() {
    platforms=""

    # --- User-level platforms ---

    # Claude Code
    if [ -d "$HOME/.claude" ]; then
        platforms="$platforms claude"
    fi

    # VS Code / GitHub Copilot (user-level skills)
    if [ -d "$HOME/.copilot" ] || command -v code >/dev/null 2>&1; then
        platforms="$platforms copilot"
    fi

    # Cursor (user-level)
    if [ -d "$HOME/.cursor" ]; then
        platforms="$platforms cursor"
    fi

    # Windsurf (detected via Codeium config)
    if [ -d "$HOME/.codeium/windsurf" ]; then
        platforms="$platforms windsurf"
    fi

    # Gemini CLI
    if [ -d "$HOME/.gemini" ]; then
        platforms="$platforms gemini"
    fi

    # Codex CLI
    if [ -d "$HOME/.codex" ] || command -v codex >/dev/null 2>&1; then
        platforms="$platforms codex"
    fi

    # Goose
    if [ -d "$HOME/.config/goose" ]; then
        platforms="$platforms goose"
    fi

    # OpenCode
    if [ -d "$HOME/.config/opencode" ]; then
        platforms="$platforms opencode"
    fi

    # Vendor-neutral (.agents/skills/) — always install here
    platforms="$platforms agents"

    # --- Project-level platforms (from cwd) ---

    # Vendor-neutral project-level
    platforms="$platforms agents-project"

    # GitHub Copilot (project-level)
    if [ -d ".github" ]; then
        platforms="$platforms copilot-project"
    fi

    # Cursor (project-level)
    if [ -d ".cursor" ]; then
        platforms="$platforms cursor-project"
    fi

    # Windsurf (project-level)
    if [ -d ".windsurf" ]; then
        platforms="$platforms windsurf-project"
    fi

    # Cline (project-level — VS Code extension)
    if [ -d ".clinerules" ]; then
        platforms="$platforms cline-project"
    fi

    # Default to Claude Code if nothing detected
    if [ -z "$platforms" ]; then
        platforms="claude"
    fi

    echo "$platforms"
}

# --- Symlink helper ---

link() {
    src="$1"
    dst="$2"
    name="$3"

    if [ "$UNINSTALL" = 1 ]; then
        if [ -L "$dst" ]; then
            if [ "$DRY_RUN" = 1 ]; then
                echo "  would remove: $dst"
            else
                rm "$dst"
                echo "  removed: $dst"
            fi
        fi
        return
    fi

    if [ -L "$dst" ] && [ "$(readlink "$dst")" = "$src" ]; then
        echo "  ok: $name (already linked)"
        return
    fi

    if [ -e "$dst" ]; then
        echo "  skip: $dst exists (not a symlink from this installer)"
        return
    fi

    # Remove broken symlinks
    if [ -L "$dst" ]; then
        rm "$dst"
    fi

    if [ "$DRY_RUN" = 1 ]; then
        echo "  would link: $dst -> $src"
    else
        mkdir -p "$(dirname "$dst")"
        ln -s "$src" "$dst"
        echo "  linked: $name -> $dst"
    fi
}

# --- Install to platform ---

install_to_platform() {
    platform="$1"
    case "$platform" in
        claude)           base="$HOME/.claude/skills" ;;
        copilot)          base="$HOME/.copilot/skills" ;;
        cursor)           base="$HOME/.cursor/rules" ;;
        windsurf)         base="$HOME/.windsurf/rules" ;;
        gemini)           base="$HOME/.gemini/skills" ;;
        codex)            base="$HOME/.codex/skills" ;;
        goose)            base="$HOME/.config/goose/skills" ;;
        opencode)         base="$HOME/.config/opencode/skills" ;;
        agents)           base="$HOME/.agents/skills" ;;
        agents-project)   base=".agents/skills" ;;
        copilot-project)  base=".github/skills" ;;
        cursor-project)   base=".cursor/rules" ;;
        windsurf-project) base=".windsurf/rules" ;;
        cline-project)    base=".clinerules" ;;
    esac

    echo "  Platform: $platform ($base)"
    link "$REPO_DIR" "$base/cliskill" "cliskill"
}

# --- Dependency installation ---

install_deps() {
    deps_dir="$(dirname "$REPO_DIR")"
    echo "Checking dependencies..."
    echo ""

    # Clarity
    if [ -d "$deps_dir/clarity" ] && [ -f "$deps_dir/clarity/SKILL.md" ]; then
        echo "  ok: /clarity found at $deps_dir/clarity"
    else
        echo "  Cloning /clarity..."
        if [ "$DRY_RUN" = 1 ]; then
            echo "  would clone: https://github.com/FrancyJGLisboa/clarity -> $deps_dir/clarity"
        else
            git clone https://github.com/FrancyJGLisboa/clarity "$deps_dir/clarity"
            echo "  cloned: /clarity"
        fi
    fi

    # Agent Skill Creator
    if [ -d "$deps_dir/agent-skill-creator" ] && [ -f "$deps_dir/agent-skill-creator/SKILL.md" ]; then
        echo "  ok: /agent-skill-creator found at $deps_dir/agent-skill-creator"
    else
        echo "  Cloning /agent-skill-creator..."
        if [ "$DRY_RUN" = 1 ]; then
            echo "  would clone: https://github.com/FrancyJGLisboa/agent-skill-creator -> $deps_dir/agent-skill-creator"
        else
            git clone https://github.com/FrancyJGLisboa/agent-skill-creator "$deps_dir/agent-skill-creator"
            echo "  cloned: /agent-skill-creator"
        fi
    fi

    echo ""

    # Install deps to platforms if they have their own installers
    if [ -f "$deps_dir/clarity/shared/install.sh" ] && [ "$DRY_RUN" = 0 ]; then
        echo "Installing /clarity to platforms..."
        sh "$deps_dir/clarity/shared/install.sh"
        echo ""
    fi
}

# --- Main ---

echo "cliskill installer"
echo "=================="
echo ""
echo "Repository: $REPO_DIR"
echo ""

if [ "$DRY_RUN" = 1 ]; then
    echo "Mode: dry run (no changes will be made)"
    echo ""
fi

if [ "$UNINSTALL" = 1 ]; then
    echo "Mode: uninstall"
    echo ""
fi

# Install dependencies first if requested
if [ "$WITH_DEPS" = 1 ] && [ "$UNINSTALL" = 0 ]; then
    install_deps
fi

# Install cliskill to all detected platforms
platforms=$(detect_platforms)

for platform in $platforms; do
    install_to_platform "$platform"
    echo ""
done

# Run dependency check
if [ "$UNINSTALL" = 0 ] && [ "$DRY_RUN" = 0 ]; then
    echo "Checking skill dependencies..."
    python3 "$REPO_DIR/scripts/check_deps.py" || true
    echo ""
    echo "Done. Restart your agent tool to pick up /cliskill."
    echo ""
    echo "Usage:"
    echo "  /cliskill <references>   — Build a verified CLI skill from API references"
    echo "  /cliskill resume         — Resume an interrupted pipeline"
fi

# Install MCP bridge dependency
if [ "$UNINSTALL" = 0 ] && [ "$DRY_RUN" = 0 ]; then
    if python3 -c "import fastmcp" 2>/dev/null; then
        echo "  ok: fastmcp (MCP bridge ready)"
    else
        echo "  Installing fastmcp for MCP bridge..."
        if command -v uv >/dev/null 2>&1; then
            uv pip install --quiet fastmcp 2>/dev/null && echo "  ok: fastmcp installed (via uv)" || {
                echo "  [info] Could not install fastmcp — MCP bridge unavailable"
                echo "         Install manually: uv pip install fastmcp"
            }
        else
            python3 -m pip install --quiet fastmcp 2>/dev/null || pip3 install --quiet fastmcp 2>/dev/null || {
                echo "  [info] Could not install fastmcp — MCP bridge unavailable"
                echo "         Install manually: pip install fastmcp"
            }
        fi
    fi
    echo ""
fi

# Generate workflow adapters for platforms that don't support SKILL.md natively
if [ "$UNINSTALL" = 0 ] && [ "$DRY_RUN" = 0 ]; then
    if echo "$platforms" | grep -q "windsurf"; then
        echo "Generating Windsurf workflow adapter..."
        python3 "$REPO_DIR/scripts/generate_windsurf_adapter.py" "$REPO_DIR" || true
        echo ""
    fi
    if echo "$platforms" | grep -q "cline"; then
        echo "Generating Cline workflow adapter..."
        python3 "$REPO_DIR/scripts/generate_cline_adapter.py" "$REPO_DIR" || true
        echo ""
    fi
fi

if [ "$DRY_RUN" = 1 ]; then
    echo "Dry run complete. No changes were made."
fi

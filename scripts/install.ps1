#Requires -Version 5.1
<#
.SYNOPSIS
    Installer for cliskill — AI-agent-friendly CLI skill framework.

.DESCRIPTION
    Installs /cliskill to all detected agent platforms via symlink (or junction/copy fallback).
    Optionally checks and installs dependencies (/clarity, /agent-skill-creator).

.PARAMETER DryRun
    Preview changes without executing.

.PARAMETER Uninstall
    Remove cliskill symlinks/junctions.

.PARAMETER WithDeps
    Also clone and install /clarity and /agent-skill-creator.

.EXAMPLE
    .\scripts\install.ps1
    .\scripts\install.ps1 -DryRun
    .\scripts\install.ps1 -Uninstall
    .\scripts\install.ps1 -WithDeps
#>

param(
    [switch]$DryRun,
    [switch]$Uninstall,
    [switch]$WithDeps
)

$ErrorActionPreference = "Stop"
$RepoDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path

# --- Platform detection ---

function Find-Platforms {
    $platforms = @()

    # Claude Code
    $claudeDir = Join-Path $env:USERPROFILE ".claude"
    if (Test-Path $claudeDir -PathType Container) {
        $platforms += "claude"
    }

    # Copilot CLI
    $copilotDir = Join-Path $env:USERPROFILE ".copilot"
    if (Test-Path $copilotDir -PathType Container) {
        $platforms += "copilot"
    }

    # Universal path (Codex CLI, Gemini CLI, Kiro, Antigravity)
    $agentsDir = Join-Path $env:USERPROFILE ".agents"
    $hasCodex = Get-Command codex -ErrorAction SilentlyContinue
    $hasGemini = Get-Command gemini -ErrorAction SilentlyContinue
    if ((Test-Path $agentsDir -PathType Container) -or $hasCodex -or $hasGemini) {
        $platforms += "universal"
    }

    # Gemini CLI
    $geminiDir = Join-Path $env:USERPROFILE ".gemini"
    if (Test-Path $geminiDir -PathType Container) {
        $platforms += "gemini"
    }

    # Goose
    $gooseDir = Join-Path $env:USERPROFILE ".config" "goose"
    if (Test-Path $gooseDir -PathType Container) {
        $platforms += "goose"
    }

    # OpenCode
    $opencodeDir = Join-Path $env:USERPROFILE ".config" "opencode"
    if (Test-Path $opencodeDir -PathType Container) {
        $platforms += "opencode"
    }

    # Default to Claude Code if nothing detected
    if ($platforms.Count -eq 0) {
        $platforms += "claude"
    }

    return $platforms
}

# --- Symlink/junction helper ---

function Install-Link {
    param(
        [string]$Source,
        [string]$Destination,
        [string]$Name
    )

    if ($Uninstall) {
        if (Test-Path $Destination) {
            $item = Get-Item $Destination -Force
            if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
                if ($DryRun) {
                    Write-Host "  would remove: $Destination"
                } else {
                    $item.Delete()
                    Write-Host "  removed: $Destination"
                }
            }
        }
        return
    }

    # Already linked correctly
    if (Test-Path $Destination) {
        $item = Get-Item $Destination -Force
        if ($item.Attributes -band [IO.FileAttributes]::ReparsePoint) {
            $target = $item.Target
            if ($target -eq $Source) {
                Write-Host "  ok: $Name (already linked)"
                return
            }
        } else {
            Write-Host "  skip: $Destination exists (not a symlink from this installer)"
            return
        }
    }

    if ($DryRun) {
        Write-Host "  would link: $Destination -> $Source"
        return
    }

    # Ensure parent directory exists
    $parentDir = Split-Path $Destination -Parent
    if (-not (Test-Path $parentDir)) {
        New-Item -ItemType Directory -Path $parentDir -Force | Out-Null
    }

    # Try symlink first (requires Developer Mode or admin on Windows 10+)
    try {
        New-Item -ItemType SymbolicLink -Path $Destination -Target $Source -Force | Out-Null
        Write-Host "  linked: $Name -> $Destination"
    } catch {
        # Fall back to directory junction (no admin required)
        try {
            cmd /c mklink /J "$Destination" "$Source" 2>&1 | Out-Null
            Write-Host "  junction: $Name -> $Destination"
        } catch {
            # Last resort: copy
            Copy-Item -Path $Source -Destination $Destination -Recurse -Force
            Write-Host "  copied: $Name -> $Destination (symlink/junction failed)"
        }
    }
}

# --- Install to platform ---

function Install-ToPlatform {
    param([string]$Platform)

    $base = switch ($Platform) {
        "claude"   { Join-Path $env:USERPROFILE ".claude" "skills" }
        "copilot"  { Join-Path $env:USERPROFILE ".copilot" "skills" }
        "universal" { Join-Path $env:USERPROFILE ".agents" "skills" }
        "gemini"   { Join-Path $env:USERPROFILE ".gemini" "skills" }
        "goose"    { Join-Path $env:USERPROFILE ".config" "goose" "skills" }
        "opencode" { Join-Path $env:USERPROFILE ".config" "opencode" "skills" }
    }

    Write-Host "  Platform: $Platform ($base)"
    Install-Link -Source $RepoDir -Destination (Join-Path $base "cliskill") -Name "cliskill"
}

# --- Dependency installation ---

function Install-Dependencies {
    $depsDir = Split-Path $RepoDir -Parent
    Write-Host "Checking dependencies..."
    Write-Host ""

    # Clarity
    $clarityDir = Join-Path $depsDir "clarity"
    $claritySkill = Join-Path $clarityDir "SKILL.md"
    if ((Test-Path $clarityDir) -and (Test-Path $claritySkill)) {
        Write-Host "  ok: /clarity found at $clarityDir"
    } else {
        Write-Host "  Cloning /clarity..."
        if ($DryRun) {
            Write-Host "  would clone: https://github.com/FrancyJGLisboa/clarity -> $clarityDir"
        } else {
            git clone https://github.com/FrancyJGLisboa/clarity $clarityDir
            Write-Host "  cloned: /clarity"
        }
    }

    # Agent Skill Creator
    $ascDir = Join-Path $depsDir "agent-skill-creator"
    $ascSkill = Join-Path $ascDir "SKILL.md"
    if ((Test-Path $ascDir) -and (Test-Path $ascSkill)) {
        Write-Host "  ok: /agent-skill-creator found at $ascDir"
    } else {
        Write-Host "  Cloning /agent-skill-creator..."
        if ($DryRun) {
            Write-Host "  would clone: https://github.com/FrancyJGLisboa/agent-skill-creator -> $ascDir"
        } else {
            git clone https://github.com/FrancyJGLisboa/agent-skill-creator $ascDir
            Write-Host "  cloned: /agent-skill-creator"
        }
    }

    Write-Host ""
}

# --- Main ---

Write-Host "cliskill installer"
Write-Host "=================="
Write-Host ""
Write-Host "Repository: $RepoDir"
Write-Host ""

if ($DryRun) {
    Write-Host "Mode: dry run (no changes will be made)"
    Write-Host ""
}

if ($Uninstall) {
    Write-Host "Mode: uninstall"
    Write-Host ""
}

# Install dependencies first if requested
if ($WithDeps -and -not $Uninstall) {
    Install-Dependencies
}

# Install cliskill to all detected platforms
$platforms = Find-Platforms

foreach ($platform in $platforms) {
    Install-ToPlatform -Platform $platform
    Write-Host ""
}

# Run dependency check
if (-not $Uninstall -and -not $DryRun) {
    Write-Host "Checking skill dependencies..."
    $checkScript = Join-Path $RepoDir "scripts" "check_deps.py"
    python3 $checkScript 2>&1 | Write-Host
    if ($LASTEXITCODE -ne 0) {
        # Try python if python3 not available
        python $checkScript 2>&1 | Write-Host
    }
    Write-Host ""
    Write-Host "Done. Restart your agent tool to pick up /cliskill."
    Write-Host ""
    Write-Host "Usage:"
    Write-Host "  /cliskill <references>   -- Build a verified CLI skill from API references"
    Write-Host "  /cliskill resume         -- Resume an interrupted pipeline"
}

if ($DryRun) {
    Write-Host "Dry run complete. No changes were made."
}

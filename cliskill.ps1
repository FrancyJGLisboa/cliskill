# cliskill — self-bootstrapping installer for Windows PowerShell.
# Clone the repo, run this file. That's it.
#
#   git clone https://github.com/FrancyJGLisboa/cliskill
#   cd cliskill
#   .\cliskill.ps1              # installs to all detected agent tools + deps
#   .\cliskill.ps1 -Uninstall   # removes everything
#   .\cliskill.ps1 -DryRun      # preview without changes

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Pass all flags through to the installer
& "$ScriptDir\scripts\install.ps1" -WithDeps @args

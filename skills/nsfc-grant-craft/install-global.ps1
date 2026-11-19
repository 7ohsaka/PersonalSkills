<#
.SYNOPSIS
    Install or update the `nsfc-grant-craft` skill globally across Antigravity and
    other Agent Skills compatible tools on this machine.

.DESCRIPTION
    Automatically syncs `nsfc-grant-craft` (excluding `.git` and `__pycache__`) to:
      - ~/.gemini/config/skills/nsfc-grant-craft   (Antigravity global)
      - ~/.agents/skills/nsfc-grant-craft          (Universal Agent Skills root)
      - ~/.claude/skills/nsfc-grant-craft          (Claude Code, if ~/.claude/skills exists)
      - ~/.codex/skills/nsfc-grant-craft           (Codex, if ~/.codex/skills exists)
#>
[CmdletBinding()]
param(
    [switch]$AntigravityOnly
)

$ErrorActionPreference = "Stop"
$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SkillName = "nsfc-grant-craft"

$Targets = @(
    (Join-Path $env:USERPROFILE ".gemini\config\skills")
)

if (-not $AntigravityOnly) {
    foreach ($rel in @(".agents\skills", ".claude\skills", ".codex\skills")) {
        $root = Join-Path $env:USERPROFILE $rel
        if (Test-Path $root) {
            $Targets += $root
        }
    }
}

function Copy-SkillClean {
    param([string]$Src, [string]$Dst)
    if (Test-Path $Dst) {
        Remove-Item -Recurse -Force $Dst
    }
    New-Item -ItemType Directory -Force -Path $Dst | Out-Null

    Get-ChildItem -Path $Src -Force | Where-Object {
        $_.Name -notin @(".git", "__pycache__", ".DS_Store")
    } | ForEach-Object {
        $destItem = Join-Path $Dst $_.Name
        if ($_.PSIsContainer) {
            Copy-SkillClean -Src $_.FullName -Dst $destItem
        } else {
            Copy-Item -Force -Path $_.FullName -Destination $destItem
        }
    }
}

Write-Host "Installing $SkillName globally..." -ForegroundColor Cyan
foreach ($root in $Targets) {
    $dest = Join-Path $root $SkillName
    Copy-SkillClean -Src $SourceDir -Dst $dest
    Write-Host "  [OK] $dest" -ForegroundColor Green
}

Write-Host "`nDone! $SkillName is now globally available across your projects and compatible agents." -ForegroundColor Green

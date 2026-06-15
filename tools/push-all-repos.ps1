# =============================================================================
# Batch Git Push Script - Template
# =============================================================================
# Fill in your repos below, then run:
#   powershell -ExecutionPolicy Bypass -File push-all-repos.ps1
# =============================================================================

# === USER: Fill in your repositories ===
$repos = @(
    # @{n="repo-name"; p="$env:CLAUDE_PROJECT_DIR\subdir"; d="description"},
    # Example:
    # @{n="my-frontend"; p="D:\projects\my-frontend"; d="My Frontend App"},
    # @{n="my-backend"; p="D:\projects\my-backend"; d="My Backend API"},
)

foreach ($r in $repos) {
    Write-Output "=== $($r.n) ==="
    cd $r.p
    ".env`n*.pem`n__pycache__/`nnode_modules/`n.DS_Store`n" | Out-File -FilePath .gitignore -Encoding utf8
    if (-not (Test-Path .git)) { git init }
    git add -A
    git commit -m "init" 2>$null
    gh repo create r-ayin/$($r.n) --public --source=. --push --description "$($r.d)"
}

Write-Output "DONE - all repos pushed"

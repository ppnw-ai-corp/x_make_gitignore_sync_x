Param(
    [string]$WorkspaceRoot = (Split-Path -Parent $PSScriptRoot)
)

$pythonExe = Join-Path $WorkspaceRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pythonExe)) {
    Write-Error "Python environment not found at $pythonExe"
    exit 1
}

$moduleRoot = Join-Path $WorkspaceRoot "x_make_gitignore_sync_x"
if (-not (Test-Path $moduleRoot)) {
    Write-Error "Module directory not found at $moduleRoot"
    exit 1
}

& $pythonExe -m x_make_gitignore_sync_x.sync --root $WorkspaceRoot @Args

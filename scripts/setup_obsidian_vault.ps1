# Run after installing the Obsidian Local REST API with MCP plugin in this vault.
param([switch]$Check)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$pluginDir = Join-Path $projectRoot '.obsidian\plugins\obsidian-local-rest-api'

if (-not (Test-Path -LiteralPath (Join-Path $pluginDir 'manifest.json')) -or
    -not (Test-Path -LiteralPath (Join-Path $pluginDir 'main.js'))) {
    throw 'Install "Local REST API with MCP" in this Obsidian vault first. See OBSIDIAN_SETUP.md.'
}

$candidates = @()
$candidates += Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
foreach ($commandName in @('py', 'python', 'python3')) {
    $command = Get-Command $commandName -ErrorAction SilentlyContinue
    if ($command) { $candidates += $command.Source }
}
$candidates += Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA 'Programs\Python') -Filter python.exe -Recurse -File -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName
$candidates += Get-ChildItem -Path 'C:\Program Files\Autodesk' -Filter mayapy.exe -Recurse -File -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName

$pythonExe = $null
foreach ($candidate in ($candidates | Select-Object -Unique)) {
    if (-not $candidate -or -not (Test-Path -LiteralPath $candidate)) { continue }
    try {
        & $candidate -c 'import sys; assert sys.version_info >= (3, 7)' 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $candidate
            break
        }
    } catch { continue }
}
if (-not $pythonExe) {
    throw 'Python 3.7+ was not found. Install Python, Codex, or Maya 2022+ and run this script again.'
}

if ($Check) {
    & $pythonExe (Join-Path $PSScriptRoot 'check_obsidian_connection.py')
    if ($LASTEXITCODE -ne 0) { throw 'Obsidian MCP check failed.' }
    exit 0
}

& $pythonExe (Join-Path $PSScriptRoot 'configure_obsidian_mcp.py')
if ($LASTEXITCODE -ne 0) { throw 'Obsidian MCP configuration failed.' }

& (Join-Path $projectRoot 'knowledge\启动实时同步.ps1')
if ($LASTEXITCODE -ne 0) { throw 'Knowledge sync could not start.' }

Write-Output 'Setup complete. Reopen the Obsidian vault, then reopen this project in Codex.'
Write-Output 'Verify with: powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_obsidian_vault.ps1 -Check'

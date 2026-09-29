# Start the repository knowledge generator and keep it watching for changes.
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$generator = Join-Path $projectRoot 'scripts\sync_obsidian_knowledge.py'
$runtimeDir = Join-Path $projectRoot 'knowledge\.knowledge_runtime'
$pidFile = Join-Path $runtimeDir 'watch.pid'
$stdoutFile = Join-Path $runtimeDir 'watch.log'
$stderrFile = Join-Path $runtimeDir 'watch.err.log'

New-Item -ItemType Directory -Path $runtimeDir -Force | Out-Null

if (Test-Path -LiteralPath $pidFile) {
    $savedPid = 0
    if ([int]::TryParse((Get-Content -LiteralPath $pidFile -Raw).Trim(), [ref]$savedPid)) {
        $running = Get-Process -Id $savedPid -ErrorAction SilentlyContinue
        if ($running -and $running.ProcessName -match 'python|mayapy') {
            Write-Output "Knowledge sync is already running (PID $savedPid)."
            exit 0
        }
    }
}

$candidates = @()
$candidates += Join-Path $env:USERPROFILE '.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
$candidates += Get-ChildItem -Path (Join-Path $env:LOCALAPPDATA 'Programs\Python') -Filter python.exe -Recurse -File -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName
$candidates += Get-ChildItem -Path 'C:\Program Files\Autodesk' -Filter mayapy.exe -Recurse -File -ErrorAction SilentlyContinue |
    Select-Object -ExpandProperty FullName

$pythonExe = $null
foreach ($candidate in $candidates) {
    if (-not $candidate -or -not (Test-Path -LiteralPath $candidate)) {
        continue
    }
    try {
        & $candidate -c 'import sys; assert sys.version_info >= (3, 7)' 2>$null
        if ($LASTEXITCODE -eq 0) {
            $pythonExe = $candidate
            break
        }
    } catch {
        continue
    }
}

if (-not $pythonExe) {
    throw 'Python 3.7+ was not found. Use Codex bundled Python or Maya 2022+ mayapy.'
}

& $pythonExe $generator
if ($LASTEXITCODE -ne 0) {
    throw 'Initial knowledge generation failed.'
}

$quotedGenerator = '"' + $generator + '"'
$process = Start-Process -FilePath $pythonExe -ArgumentList @($quotedGenerator, '--watch') -WorkingDirectory $projectRoot -WindowStyle Hidden -RedirectStandardOutput $stdoutFile -RedirectStandardError $stderrFile -PassThru
Set-Content -LiteralPath $pidFile -Value $process.Id -Encoding ASCII
Write-Output "Knowledge sync started (PID $($process.Id))."
Write-Output "Open this folder as a vault in Obsidian: $projectRoot"

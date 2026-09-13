param(
    [Parameter(Position = 0)]
    [string]$CommitMessage = "Update FlooferCore"
)

$ErrorActionPreference = "Stop"

# ============================================================
# PATHS
# ============================================================

$ProjectRoot = $PSScriptRoot
$PidFile = Join-Path $ProjectRoot ".floofercore.pid"
$LogDirectory = Join-Path $ProjectRoot "logs"
$LogFile = Join-Path $LogDirectory "floofercore.log"
$ErrorLogFile = Join-Path $LogDirectory "floofercore-error.log"

Set-Location $ProjectRoot


Write-Host ""
Write-Host "============================================================"
Write-Host " FlooferCore Deployment"
Write-Host "============================================================"
Write-Host ""


# ============================================================
# GIT STATUS
# ============================================================

Write-Host "[1/5] Checking repository..."

git status --short

if ($LASTEXITCODE -ne 0) {
    throw "Git status failed."
}


# ============================================================
# GIT ADD
# ============================================================

Write-Host ""
Write-Host "[2/5] Staging changes..."

git add .

if ($LASTEXITCODE -ne 0) {
    throw "git add failed."
}


# ============================================================
# GIT COMMIT
# ============================================================

Write-Host ""
Write-Host "[3/5] Creating commit..."

$StagedChanges = git diff --cached --name-only

if ($StagedChanges) {

    git commit -m $CommitMessage

    if ($LASTEXITCODE -ne 0) {
        throw "git commit failed."
    }

}
else {

    Write-Host "No changes to commit."

}


# ============================================================
# GIT PUSH
# ============================================================

Write-Host ""
Write-Host "[4/5] Pushing to GitHub..."

git push

if ($LASTEXITCODE -ne 0) {
    throw "git push failed."
}


# ============================================================
# STOP EXISTING BOT
# ============================================================

Write-Host ""
Write-Host "[5/5] Restarting FlooferCore..."

if (Test-Path $PidFile) {

    $OldPid = Get-Content $PidFile

    if ($OldPid) {

        $OldProcess = Get-Process `
            -Id $OldPid `
            -ErrorAction SilentlyContinue

        if ($OldProcess) {

            Write-Host "Stopping old FlooferCore process (PID $OldPid)..."

            Stop-Process `
                -Id $OldPid `
                -Force

            Start-Sleep -Seconds 1

        }
        else {

            Write-Host "Old FlooferCore process is no longer running."

        }
    }

    Remove-Item `
        $PidFile `
        -Force `
        -ErrorAction SilentlyContinue
}


# ============================================================
# LOG DIRECTORY
# ============================================================

if (-not (Test-Path $LogDirectory)) {

    New-Item `
        -ItemType Directory `
        -Path $LogDirectory | Out-Null

}


# ============================================================
# START BOT
# ============================================================

Write-Host "Starting FlooferCore..."

$BotProcess = Start-Process `
    -FilePath "python" `
    -ArgumentList "main.py" `
    -WorkingDirectory $ProjectRoot `
    -RedirectStandardOutput $LogFile `
    -RedirectStandardError $ErrorLogFile `
    -WindowStyle Hidden `
    -PassThru


$BotProcess.Id |
    Out-File `
        -FilePath $PidFile `
        -Encoding ascii


Start-Sleep -Seconds 2


# ============================================================
# VERIFY
# ============================================================

$RunningProcess = Get-Process `
    -Id $BotProcess.Id `
    -ErrorAction SilentlyContinue


if (-not $RunningProcess) {

    Write-Host ""
    Write-Host "FlooferCore failed to start."

    if (Test-Path $ErrorLogFile) {

        Write-Host ""
        Write-Host "Error log:"
        Write-Host "------------------------------------------------------------"

        Get-Content $ErrorLogFile -Tail 20

    }

    exit 1
}


# ============================================================
# COMPLETE
# ============================================================

Write-Host ""
Write-Host "============================================================"
Write-Host " Deployment complete"
Write-Host "============================================================"

Write-Host ""
Write-Host "Commit: $CommitMessage"
Write-Host "Bot PID: $($BotProcess.Id)"
Write-Host "Log: $LogFile"
Write-Host ""

Write-Host "FlooferCore is back online."
Write-Host ""
# Nexus Terminal - PATH Setup Script
# Adds the Nexus Terminal folder to user PATH and ensures .py is in PATHEXT,
# so the 'nt' command works from anywhere (without batch file side effects).
#
# Usage: Right-click this file -> "Run with PowerShell"
#   or:   powershell -ExecutionPolicy Bypass -File install.ps1

$folder = $PSScriptRoot

try {
    Write-Host ""
    Write-Host "Nexus Terminal - Installation" -ForegroundColor Cyan
    Write-Host "==============================" -ForegroundColor Cyan

    # --- 1. Add folder to user PATH ---
    $currentPath = [Environment]::GetEnvironmentVariable("PATH", "User")
    $inPath = ($currentPath -split ";" | Where-Object { $_ -ieq $folder }).Count -gt 0

    if ($inPath) {
        Write-Host "[OK]   Folder already in PATH." -ForegroundColor Yellow
    } else {
        $newPath = if ($currentPath) { "$currentPath;$folder" } else { $folder }
        [Environment]::SetEnvironmentVariable("PATH", $newPath, "User")
        Write-Host "[OK]   Added '$folder' to user PATH." -ForegroundColor Green
        Write-Host "[i]    Restart your terminal for changes to take effect." -ForegroundColor Cyan
    }

    # --- 2. Ensure .PY is in PATHEXT (so 'nt' finds nt.py) ---
    # IMPORTANT: On Windows, User PATHEXT OVERRIDES Machine PATHEXT (not concatenated like PATH).
    # So when creating a User PATHEXT, we must include ALL Machine extensions + .PY.
    $userPathext = [Environment]::GetEnvironmentVariable("PATHEXT", "User")
    $machinePathext = [Environment]::GetEnvironmentVariable("PATHEXT", "Machine")
    $allPathext = "$userPathext;$machinePathext"

    if ($allPathext -match '\.PY') {
        Write-Host "[OK]   .PY already in PATHEXT." -ForegroundColor Yellow
    } else {
        # Base must be the full Machine PATHEXT (or existing User PATHEXT if set)
        # to avoid overriding system extensions like .EXE, .CMD, etc.
        $base = if ($userPathext) { $userPathext } else { $machinePathext }
        $newPathext = "$base;.PY"
        [Environment]::SetEnvironmentVariable("PATHEXT", $newPathext, "User")
        Write-Host "[OK]   Added .PY to PATHEXT." -ForegroundColor Green
        Write-Host "[i]    Restart your terminal for changes to take effect." -ForegroundColor Cyan
    }

    # --- 3. Verify Python is available ---
    $python = Get-Command python -ErrorAction SilentlyContinue
    if ($python) {
        Write-Host "[OK]   Python found: $($python.Source)" -ForegroundColor Green
    } else {
        Write-Host "[!!]   Python not found in PATH. Install Python 3.7+ from python.org." -ForegroundColor Red
        Write-Host "       Make sure to check 'Add Python to PATH' during installation." -ForegroundColor Yellow
    }

    # --- 4. Verify nt.py exists ---
    if (Test-Path "$folder\nt.py") {
        Write-Host "[OK]   nt.py found. The 'nt' command is ready." -ForegroundColor Green
    } else {
        Write-Host "[!!]   nt.py not found in $folder" -ForegroundColor Red
    }

} catch {
    Write-Host ""
    Write-Host "[!!]   Error: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press Enter to exit..." -ForegroundColor DarkGray
Read-Host

[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$OverlayArguments
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$ActivateScript = Join-Path $ProjectRoot ".venv\Scripts\Activate.ps1"

if (-not (Test-Path $ActivateScript)) {
    throw "The virtual environment is missing. Run .\install.ps1 first."
}

Push-Location $ProjectRoot
try {
    . $ActivateScript
    & python -m radar_overlay.main @OverlayArguments
    if ($LASTEXITCODE -ne 0) {
        throw "The overlay stopped with exit code $LASTEXITCODE."
    }
}
finally {
    Pop-Location
}

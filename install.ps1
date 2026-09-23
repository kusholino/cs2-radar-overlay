[CmdletBinding()]
param(
    [switch]$SkipDevDependencies
)

$ErrorActionPreference = "Stop"

$ProjectRoot = $PSScriptRoot
$VirtualEnvironment = Join-Path $ProjectRoot ".venv"
$VirtualPython = Join-Path $VirtualEnvironment "Scripts\python.exe"
$ConfigPath = Join-Path $ProjectRoot "config.toml"
$ExampleConfigPath = Join-Path $ProjectRoot "config.example.toml"

function Get-PythonCommand {
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if ($pythonCommand) {
        return ,@($pythonCommand.Source)
    }

    $pyLauncher = Get-Command py -ErrorAction SilentlyContinue
    if ($pyLauncher) {
        return ,@($pyLauncher.Source, "-3.11")
    }

    throw "Python 3.11 or later was not found. Install it from https://www.python.org/downloads/windows/ and run this script again."
}

function Invoke-PythonCommand {
    param(
        [string[]]$Arguments
    )

    & $VirtualPython @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed with exit code $LASTEXITCODE."
    }
}

Push-Location $ProjectRoot
try {
    $pythonCommand = Get-PythonCommand
    $pythonArguments = @()
    if ($pythonCommand.Count -gt 1) {
        $pythonArguments = $pythonCommand[1..($pythonCommand.Count - 1)]
    }

    & $pythonCommand[0] @pythonArguments -c "import sys; assert sys.version_info >= (3, 11), sys.version"
    if ($LASTEXITCODE -ne 0) {
        throw "Python 3.11 or later is required."
    }

    if (-not (Test-Path $VirtualPython)) {
        Write-Host "Creating virtual environment in .venv ..."
        & $pythonCommand[0] @pythonArguments -m venv $VirtualEnvironment
        if ($LASTEXITCODE -ne 0) {
            throw "Virtual-environment creation failed with exit code $LASTEXITCODE."
        }
    }

    Write-Host "Upgrading pip ..."
    Invoke-PythonCommand -Arguments @("-m", "pip", "install", "--upgrade", "pip")

    $installTarget = if ($SkipDevDependencies) { "." } else { ".[dev]" }
    Write-Host "Installing project dependencies ..."
    Invoke-PythonCommand -Arguments @("-m", "pip", "install", "-e", $installTarget)

    if (-not (Test-Path $ConfigPath)) {
        Copy-Item $ExampleConfigPath $ConfigPath
        Write-Host "Created config.toml from config.example.toml."
    }

    $PresetsPath = Join-Path $ProjectRoot "presets"
    if (-not (Test-Path $PresetsPath)) {
        New-Item -ItemType Directory -Path $PresetsPath | Out-Null
    }

    Write-Host "Setup complete. Start the overlay with: .\.venv\Scripts\python.exe -m radar_overlay.main --config config.toml"
}
finally {
    Pop-Location
}

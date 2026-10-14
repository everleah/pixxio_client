[CmdletBinding()]
param(
    [switch]$BuildOnly,
    [string]$Python = (Join-Path $PSScriptRoot '.venv\Scripts\python.exe'),
    [string]$TokenPath = (Join-Path $env:APPDATA 'pixxio_client\pypi-token.xml')
)

$ErrorActionPreference = 'Stop'

function Invoke-Python {
    param([string[]]$Arguments)

    & $Python @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed (exit $LASTEXITCODE): $($Arguments -join ' ')"
    }
}

if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Python interpreter not found: $Python. Create .venv or pass -Python."
}
$Python = (Resolve-Path -LiteralPath $Python).Path

if (-not $BuildOnly) {
    if (-not (Test-Path -LiteralPath $TokenPath -PathType Leaf)) {
        throw "PyPI credential not found: $TokenPath. See the release instructions in README.md."
    }
    $credential = Import-Clixml -LiteralPath $TokenPath
    if ($credential -isnot [System.Management.Automation.PSCredential] -or
        $credential.UserName -ne '__token__' -or
        -not $credential.GetNetworkCredential().Password.StartsWith('pypi-')) {
        throw "Invalid PyPI credential in $TokenPath."
    }
}

$buildDirectory = Join-Path ([System.IO.Path]::GetTempPath()) ('pixxio-release-' + [guid]::NewGuid().ToString('N'))
$previousUsername = $env:TWINE_USERNAME
$previousPassword = $env:TWINE_PASSWORD

Push-Location -LiteralPath $PSScriptRoot
try {
    Invoke-Python -Arguments @('-m', 'unittest', 'tests.response_fields_injection_checks', 'tests.test_webhook_parser_generalized', '-v')
    Invoke-Python -Arguments @('-m', 'build', '--outdir', $buildDirectory)

    $artifacts = @(Get-ChildItem -LiteralPath $buildDirectory -File)
    $wheels = @($artifacts | Where-Object { $_.Name.EndsWith('.whl') })
    $sources = @($artifacts | Where-Object { $_.Name.EndsWith('.tar.gz') })
    if ($wheels.Count -ne 1 -or $sources.Count -ne 1 -or $artifacts.Count -ne 2) {
        throw 'Expected exactly one wheel and one source distribution.'
    }
    $artifactPaths = @($artifacts | ForEach-Object { $_.FullName })
    Invoke-Python -Arguments (@('-m', 'twine', 'check', '--strict') + $artifactPaths)

    $outputDirectory = Join-Path $PSScriptRoot 'build_output\pypi'
    New-Item -ItemType Directory -Path $outputDirectory -Force | Out-Null
    foreach ($artifact in $artifacts) {
        Copy-Item -LiteralPath $artifact.FullName -Destination $outputDirectory -Force
    }
    Write-Output "Verified release artifacts: $outputDirectory"

    if (-not $BuildOnly) {
        $env:TWINE_USERNAME = '__token__'
        $env:TWINE_PASSWORD = $credential.GetNetworkCredential().Password
        Invoke-Python -Arguments (@(
            '-m', 'twine', 'upload', '--non-interactive',
            '--repository-url', 'https://upload.pypi.org/legacy/'
        ) + $artifactPaths)
        Write-Output 'Published to https://pypi.org/project/pixxio-client/'
    }
}
finally {
    $env:TWINE_USERNAME = $previousUsername
    $env:TWINE_PASSWORD = $previousPassword
    Pop-Location
    if (Test-Path -LiteralPath $buildDirectory) {
        Remove-Item -LiteralPath $buildDirectory -Recurse -Force
    }
}

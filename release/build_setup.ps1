# build_setup.ps1
# Compila o instalador Inno Setup (installer.iss) e gera Setup.exe na pasta release

param(
    [string]$ISCCPath = "",
    [switch]$Verbose
)

$ErrorActionPreference = 'Stop'

function Info($msg) { Write-Host "[INFO] $msg" -ForegroundColor Cyan }
function Fail($msg) { Write-Host "[ERROR] $msg" -ForegroundColor Red; exit 1 }

$root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent
$iss = Join-Path $root 'installer.iss'
$releaseDir = Join-Path $root 'release'

if (-not (Test-Path $iss)) { Fail "installer.iss não encontrado em $root" }

# Detectar ISCC.exe
$paths = @(
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)
if ($ISCCPath -and (Test-Path $ISCCPath)) {
    $iscc = $ISCCPath
} else {
    $iscc = $null
    foreach ($p in $paths) { if (Test-Path $p) { $iscc = $p; break } }
}

if (-not $iscc) {
    Fail "ISCC.exe não encontrado. Instale Inno Setup 6: https://jrsoftware.org/isdl.php"
}

Info "Usando ISCC: $iscc"

# Compilar
& $iscc $iss | ForEach-Object { if ($Verbose) { Write-Host $_ } }

# Estimar saída (usando defines do .iss)
$MyAppName = (Get-Content $iss | Where-Object { $_ -match '^#define MyAppName ' } | ForEach-Object { ($_ -split '"')[1] })
$MyAppVersion = (Get-Content $iss | Where-Object { $_ -match '^#define MyAppVersion ' } | ForEach-Object { ($_ -split '"')[1] })
$setup = Join-Path $releaseDir "$MyAppName-Setup-$MyAppVersion.exe"
if (-not (Test-Path $setup)) {
    # Fallback: pegar o .exe mais recente na pasta release
    $candidate = Get-ChildItem $releaseDir -Filter '*.exe' | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    if ($candidate) { $setup = $candidate.FullName }
}

if (-not (Test-Path $setup)) { Fail "Setup.exe não foi gerado." }

$sizeMB = [Math]::Round(((Get-Item $setup).Length / 1MB), 2)
Info "Setup gerado: $setup ($sizeMB MB)"
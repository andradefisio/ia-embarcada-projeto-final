param([string]$IdfProfile = $env:ESP_IDF_PROFILE)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Get-Command idf.py -ErrorAction SilentlyContinue)) {
    if (-not $IdfProfile -and (Test-Path '.local/esp-idf-profile.ps1')) { $IdfProfile = '.local/esp-idf-profile.ps1' }
    if (-not $IdfProfile -or -not (Test-Path -LiteralPath $IdfProfile)) { throw 'Abra um terminal ESP-IDF ou informe -IdfProfile (ou ESP_IDF_PROFILE).' }
    . $IdfProfile
}
if (-not (Test-Path main/generated/model_data.h)) { throw 'Execute python scripts/train.py antes de compilar.' }
if (-not (Test-Path main/generated/test_data.h)) { throw 'Execute python scripts/export_test_data.py antes de compilar.' }
idf.py build
if ($LASTEXITCODE -ne 0) { throw 'Falha na compilacao ESP-IDF.' }
idf.py merge-bin
if ($LASTEXITCODE -ne 0) { throw 'Falha ao gerar imagem completa.' }

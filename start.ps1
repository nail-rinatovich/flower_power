$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
$pythonPath = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonPath)) {
    throw 'Сначала создайте .venv и установите зависимости. Инструкция в README.md.'
}
& $pythonPath manage.py migrate
if ($LASTEXITCODE -ne 0) { throw 'Не удалось применить миграции.' }
& $pythonPath manage.py runserver 127.0.0.1:8011

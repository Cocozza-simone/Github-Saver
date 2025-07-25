# Auto GitHub Saver - Script PowerShell
# Salva automaticamente il progetto corrente su GitHub

param(
    [string]$Project = $null,
    [string]$Message = $null,
    [switch]$NoBackup = $false
)

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "    Auto GitHub Saver" -ForegroundColor Yellow
Write-Host "    Salvataggio automatico su GitHub" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Controlla se Python è installato
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✅ Python trovato: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Errore: Python non trovato!" -ForegroundColor Red
    Write-Host "💡 Installa Python da https://python.org" -ForegroundColor Yellow
    Read-Host "Premi Enter per uscire"
    exit 1
}

# Controlla se esiste il file auto_saver.py
if (-not (Test-Path "auto_saver.py")) {
    Write-Host "❌ Errore: auto_saver.py non trovato!" -ForegroundColor Red
    Write-Host "💡 Assicurati di essere nella cartella corretta" -ForegroundColor Yellow
    Read-Host "Premi Enter per uscire"
    exit 1
}

# Prepara i parametri
$scriptArgs = @()
if ($Project) {
    $scriptArgs += "--project"
    $scriptArgs += $Project
}
if ($Message) {
    $scriptArgs += "--message"
    $scriptArgs += $Message
}
if ($NoBackup) {
    $scriptArgs += "--no-backup"
}

# Esegui il salvataggio automatico
Write-Host "🚀 Avvio salvataggio automatico..." -ForegroundColor Blue
Write-Host ""

try {
    if ($scriptArgs.Count -gt 0) {
        & python auto_saver.py @scriptArgs
    } else {
        & python auto_saver.py
    }
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "✅ Salvataggio completato con successo!" -ForegroundColor Green
        Write-Host "🌐 Controlla il tuo repository su GitHub" -ForegroundColor Cyan
        Start-Sleep -Seconds 2
    } else {
        throw "Processo terminato con codice di errore $LASTEXITCODE"
    }
} catch {
    Write-Host ""
    Write-Host "❌ Salvataggio fallito: $($_.Exception.Message)" -ForegroundColor Red
    Read-Host "Premi Enter per uscire"
    exit 1
}

@echo off
REM Auto GitHub Saver - Script Batch per Windows
REM Salva automaticamente il progetto corrente su GitHub

echo.
echo ========================================
echo    Auto GitHub Saver
echo    Salvataggio automatico su GitHub
echo ========================================
echo.

REM Controlla se Python è installato
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Errore: Python non trovato!
    echo 💡 Installa Python da https://python.org
    pause
    exit /b 1
)

REM Controlla se esiste il file auto_saver.py
if not exist "auto_saver.py" (
    echo ❌ Errore: auto_saver.py non trovato!
    echo 💡 Assicurati di essere nella cartella corretta
    pause
    exit /b 1
)

REM Esegui il salvataggio automatico
echo 🚀 Avvio salvataggio automatico...
echo.

REM Passa tutti i parametri allo script Python
python auto_saver.py %*

REM Controlla il risultato
if errorlevel 1 (
    echo.
    echo ❌ Salvataggio fallito!
    pause
    exit /b 1
) else (
    echo.
    echo ✅ Salvataggio completato con successo!
    echo 🌐 Controlla il tuo repository su GitHub
    timeout /t 3 >nul
)

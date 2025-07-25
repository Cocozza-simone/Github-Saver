# 🚀 Auto GitHub Saver - Modalità Completamente Automatica

Sistema di salvataggio automatico su GitHub senza richiedere alcun input dall'utente.

## ✨ Caratteristiche

- **Completamente automatico** - Nessuna domanda, nessun input richiesto
- **Rilevamento intelligente** - Analizza automaticamente il tipo di progetto
- **Commit intelligenti** - Genera messaggi di commit appropriati
- **Backup automatici** - Mantiene copie di sicurezza locali
- **Multi-piattaforma** - Funziona su Windows, macOS e Linux

## 🔧 Setup Iniziale

### 1. Token GitHub
Prima di tutto, devi configurare il token GitHub:

**Opzione A - Variabile d'ambiente:**
```bash
# Windows (Command Prompt)
set GITHUB_TOKEN=your_personal_access_token

# Windows (PowerShell)
$env:GITHUB_TOKEN="your_personal_access_token"

# Linux/macOS
export GITHUB_TOKEN=your_personal_access_token
```

**Opzione B - File .env:**
Crea un file `.env` nella cartella del progetto:
```
GITHUB_TOKEN=your_personal_access_token
```

### 2. Dipendenze Python
```bash
pip install requests colorama rich
```

## 🚀 Utilizzo

### Metodo 1: Script Python Diretto
```bash
# Modalità interattiva - chiede quale cartella salvare
python auto_saver.py

# Specifica cartella direttamente
python auto_saver.py --project "C:\path\to\my\project"

# Con messaggio personalizzato
python auto_saver.py --project "C:\path\to\my\project" --message "Il mio commit"

# Senza backup
python auto_saver.py --project "C:\path\to\my\project" --no-backup
```

### Metodo 2: Script Batch (Windows)
```cmd
# Modalità interattiva
save_to_github.bat

# Con parametri
save_to_github.bat --project "C:\path\to\my\project"
save_to_github.bat --project "C:\path\to\my\project" --message "Il mio commit"
```

### Metodo 3: Script PowerShell (Windows)
```powershell
# Modalità interattiva
.\Save-ToGitHub.ps1

# Specifica cartella
.\Save-ToGitHub.ps1 -Project "C:\path\to\my\project"

# Con messaggio personalizzato
.\Save-ToGitHub.ps1 -Project "C:\path\to\my\project" -Message "Il mio commit"

# Senza backup
.\Save-ToGitHub.ps1 -Project "C:\path\to\my\project" -NoBackup
```

## 🤖 Cosa Fa Automaticamente

1. **Analizza il progetto** - Rileva il tipo di progetto (Python, JavaScript, ecc.)
2. **Genera commit intelligente** - Crea un messaggio appropriato basato sui cambiamenti
3. **Inizializza Git** - Se necessario, inizializza il repository
4. **Crea repository GitHub** - Se non esiste, lo crea automaticamente
5. **Commit e Push** - Salva tutti i cambiamenti su GitHub
6. **Gestisce versioning** - Aggiorna automaticamente i numeri di versione
7. **Backup locale** - Mantiene copie di sicurezza

## 📋 Esempi di Messaggi di Commit Automatici

- `feat: Update main.py` - Per singoli file
- `feat: Update main.py, utils.py, config.json` - Per pochi file
- `feat: Update 15 files` - Per molti file
- `fix: Auto-save project changes` - Quando non ci sono file specifici

## 🔄 Automazione Avanzata

### Esecuzione Programmata (Windows)
Puoi programmare l'esecuzione automatica usando Task Scheduler:

1. Apri Task Scheduler
2. Crea attività di base
3. Imposta trigger (es. ogni ora, ogni giorno)
4. Azione: Avvia programma
5. Programma: `C:\path\to\save_to_github.bat`

### Script di Monitoraggio
Crea uno script che monitora i cambiamenti e salva automaticamente:

```python
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AutoSaveHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if not event.is_directory:
            print(f"File modificato: {event.src_path}")
            # Attendi 5 secondi per evitare salvataggi multipli
            time.sleep(5)
            subprocess.run(["python", "auto_saver.py"])

# Monitora la cartella corrente
observer = Observer()
observer.schedule(AutoSaveHandler(), ".", recursive=True)
observer.start()

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
observer.join()
```

## ⚙️ Configurazione

Il sistema usa le seguenti impostazioni predefinite:
- **Username GitHub**: Cocozza-simone (modificabile in `saver_pro.py`)
- **Backup**: Abilitato (cartella `~/.github_saver_backups`)
- **Versioning**: Automatico (incrementa patch version)
- **Branch**: master/main (rilevato automaticamente)

## 🛠️ Risoluzione Problemi

### Token non trovato
```
❌ Errore: Token GitHub non trovato!
```
**Soluzione**: Configura il token come descritto nel setup

### Repository già esistente
Il sistema gestisce automaticamente repository esistenti e li aggiorna.

### Problemi di encoding
Il sistema è stato ottimizzato per evitare problemi di encoding su Windows.

### Nessun cambiamento da committare
```
ℹ️ No changes to commit
```
Questo è normale quando non ci sono modifiche da salvare.

## 📞 Supporto

Per problemi o domande, controlla:
1. Che il token GitHub sia configurato correttamente
2. Che Python e le dipendenze siano installate
3. Che tu abbia i permessi per creare repository su GitHub

## 🎯 Vantaggi della Modalità Automatica

- ✅ **Zero interruzioni** - Nessuna domanda durante il processo
- ✅ **Veloce** - Salvataggio in pochi secondi
- ✅ **Intelligente** - Rileva automaticamente cosa fare
- ✅ **Sicuro** - Mantiene backup e versioning
- ✅ **Flessibile** - Funziona con qualsiasi tipo di progetto

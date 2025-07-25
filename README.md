# GitHub Saver - Script Automatico per GitHub

Script Python che automatizza completamente il salvataggio di progetti su GitHub con versioning automatico.

## 🚀 Caratteristiche

- ✅ **Completamente automatizzato**: Crea repository se non esiste
- 📦 **Versioning automatico**: Incrementa automaticamente la versione (v1.0.0, v1.0.1, etc.)
- 🔧 **Creazione repository**: Supporta GitHub CLI e API GitHub
- 📝 **Commit intelligenti**: Messaggi automatici con timestamp e versione
- 🌐 **Cross-platform**: Funziona su Windows, Mac, Linux

## 📋 Prerequisiti

1. **Python 3.6+**
2. **Git** installato e configurato
3. **Opzionale**: GitHub CLI per creazione automatica repository

## 🛠️ Installazione

### Metodo 1: GitHub CLI (Raccomandato)
```bash
# Windows
winget install GitHub.cli

# Mac
brew install gh

# Linux
sudo apt install gh
```

### Metodo 2: Token GitHub API
1. Vai su https://github.com/settings/tokens
2. Crea un nuovo token con permessi `repo`
3. Crea file `.env` con:
```
GITHUB_TOKEN=your_token_here
```

## 🎯 Utilizzo

### Salvataggio automatico con versioning
```bash
python github_saver.py
```

### Salvataggio con messaggio personalizzato
```bash
python github_saver.py "Aggiunta nuova funzionalità"
```

## 📁 File generati

- `.version`: Contiene la versione corrente del progetto
- `.env.example`: Template per configurazione token GitHub

## 🔄 Come funziona

1. **Inizializza Git** se necessario
2. **Aggiunge tutti i file** al repository
3. **Genera versione automatica** (v1.0.0 → v1.0.1)
4. **Crea commit** con messaggio e versione
5. **Controlla se repository esiste** su GitHub
6. **Crea repository** automaticamente se non esiste
7. **Carica tutto** su GitHub

## 📊 Esempio di output

```
🚀 Salvando 'mio-progetto' su GitHub...
📝 Aggiungendo file...
🔧 Repository non esiste, lo creo automaticamente...
✅ Repository creato con GitHub CLI!
📦 Versione: v1.0.1
```

## ⚙️ Configurazione

### Username GitHub
Modifica la riga 10 nel file:
```python
def __init__(self, username="TUO_USERNAME"):
```

### Formato versioning
Il formato predefinito è `v1.0.0`. Puoi modificare il metodo `get_next_version()` per personalizzarlo.

## 🐛 Risoluzione problemi

### Repository non creato automaticamente
1. Installa GitHub CLI: `winget install GitHub.cli`
2. Oppure configura token GitHub API
3. Oppure crea manualmente su https://github.com/new

### Errori di permessi
Assicurati che Git sia configurato:
```bash
git config --global user.name "Tuo Nome"
git config --global user.email "tua@email.com"
```

## 📝 Licenza

Questo script è open source e può essere modificato liberamente.
# github-simply

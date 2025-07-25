#!/bin/bash

# Tool per salvare progetto su GitHub personale
set -e

# Configurazione
GITHUB_USERNAME="Cocozza-simone"  # Sostituisci con il tuo username
PROJECT_NAME=$(basename "$PWD")
REMOTE_NAME="origin"

# Colori per output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🚀 Deploy Tool per GitHub${NC}"
echo "Progetto: $PROJECT_NAME"

# Verifica se è un repo git
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}Inizializzo repository Git...${NC}"
    git init
fi

# Aggiungi tutti i file
echo -e "${YELLOW}Aggiungendo file...${NC}"
git add .

# Commit con timestamp
COMMIT_MSG="Auto-save: $(date '+%Y-%m-%d %H:%M:%S')"
if [ ! -z "$1" ]; then
    COMMIT_MSG="$1"
fi

git commit -m "$COMMIT_MSG" || echo "Nessun cambiamento da committare"

# Verifica se il remote esiste
if ! git remote get-url $REMOTE_NAME > /dev/null 2>&1; then
    echo -e "${YELLOW}Configurando remote GitHub...${NC}"
    git remote add $REMOTE_NAME "https://github.com/$GITHUB_USERNAME/$PROJECT_NAME.git"
fi

# Push
echo -e "${YELLOW}Caricando su GitHub...${NC}"
git push -u $REMOTE_NAME main 2>/dev/null || git push -u $REMOTE_NAME master

echo -e "${GREEN}✅ Progetto salvato su: https://github.com/$GITHUB_USERNAME/$PROJECT_NAME${NC}"
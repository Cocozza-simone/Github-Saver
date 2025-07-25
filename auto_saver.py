#!/usr/bin/env python3
"""
Auto GitHub Saver - Versione completamente automatica
Salva automaticamente il progetto corrente su GitHub senza richiedere input
"""

import os
import sys
import asyncio
from pathlib import Path

# Importa la classe principale
from saver_pro import GitHubSaverPro, console

def main():
    """Funzione principale completamente automatica."""
    
    console.print("🚀 [bold blue]Auto GitHub Saver[/bold blue] - Modalità Automatica")
    
    # Verifica che esista un token GitHub
    token_sources = [
        os.getenv('GITHUB_TOKEN'),
        Path('.env').exists() and 'GITHUB_TOKEN=' in Path('.env').read_text()
    ]
    
    if not any(token_sources):
        console.print("❌ [red]Errore: Token GitHub non trovato![/red]")
        console.print("💡 [yellow]Soluzioni:[/yellow]")
        console.print("   1. Imposta la variabile d'ambiente: set GITHUB_TOKEN=your_token")
        console.print("   2. Crea un file .env con: GITHUB_TOKEN=your_token")
        sys.exit(1)
    
    async def auto_save():
        try:
            # Crea l'istanza del saver
            saver = GitHubSaverPro()
            
            # Salva automaticamente
            await saver.save_project(
                commit_message=None,  # Genera automaticamente
                interactive=False,    # Nessuna interazione
                backup=True          # Mantieni backup
            )
            
            console.print("✅ [green]Progetto salvato automaticamente su GitHub![/green]")
            
        except Exception as e:
            console.print(f"❌ [red]Errore durante il salvataggio: {e}[/red]")
            sys.exit(1)
    
    # Esegui il salvataggio automatico
    asyncio.run(auto_save())

if __name__ == "__main__":
    main()

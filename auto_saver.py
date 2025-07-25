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

    # Gestisci parametri da riga di comando
    import argparse
    parser = argparse.ArgumentParser(description='Auto GitHub Saver')
    parser.add_argument('--project', '-p', help='Percorso della cartella del progetto')
    parser.add_argument('--message', '-m', help='Messaggio di commit personalizzato')
    parser.add_argument('--no-backup', action='store_true', help='Salta la creazione del backup')

    args = parser.parse_args()

    # Verifica autenticazione GitHub (token o CLI)
    has_token = bool(os.getenv('GITHUB_TOKEN')) or (Path('.env').exists() and 'GITHUB_TOKEN=' in Path('.env').read_text())

    # Verifica GitHub CLI
    has_gh_cli = False
    try:
        import subprocess
        result = subprocess.run(['gh', 'auth', 'status'], capture_output=True, text=True)
        has_gh_cli = result.returncode == 0
    except:
        pass

    if not (has_token or has_gh_cli):
        console.print("❌ [red]Errore: Nessun metodo di autenticazione GitHub trovato![/red]")
        console.print("💡 [yellow]Soluzioni:[/yellow]")
        console.print("   [bold]Opzione 1: GitHub CLI (Raccomandato)[/bold]")
        console.print("   - Esegui: [cyan]gh auth login[/cyan]")
        console.print("   [bold]Opzione 2: Token Personale[/bold]")
        console.print("   - Imposta variabile: [cyan]set GITHUB_TOKEN=your_token[/cyan]")
        console.print("   - O crea file .env con: [cyan]GITHUB_TOKEN=your_token[/cyan]")
        sys.exit(1)
    elif has_gh_cli:
        console.print("✅ [green]GitHub CLI autenticato[/green]")
    elif has_token:
        console.print("✅ [green]Token GitHub trovato[/green]")
    
    async def auto_save():
        try:
            # Crea l'istanza del saver
            if args.project:
                console.print(f"📁 [cyan]Usando cartella specificata: {args.project}[/cyan]")
                saver = GitHubSaverPro(project_path=args.project)
            else:
                console.print("🎯 [yellow]Seleziona la cartella del progetto da salvare:[/yellow]")
                saver = GitHubSaverPro()

            # Salva automaticamente (tutto il resto è automatico)
            await saver.save_project(
                commit_message=args.message,  # Usa messaggio personalizzato se fornito
                interactive=False,            # Nessuna altra interazione
                backup=not args.no_backup    # Backup a meno che non sia disabilitato
            )

            console.print("✅ [green]Progetto salvato automaticamente su GitHub![/green]")

        except Exception as e:
            console.print(f"❌ [red]Errore durante il salvataggio: {e}[/red]")
            sys.exit(1)

    # Esegui il salvataggio automatico
    asyncio.run(auto_save())

if __name__ == "__main__":
    main()

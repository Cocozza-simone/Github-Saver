#!/usr/bin/env python3
import os
import subprocess
import sys
import json
import re
from datetime import datetime

class GitHubSaver:
    def __init__(self, username="Cocozza-simone", token=None):
        self.username = username or input("GitHub username: ")
        # Replace spaces with hyphens for GitHub repository name
        self.project_name = os.path.basename(os.getcwd()).replace(" ", "-")
        self.token = token or os.getenv('GITHUB_TOKEN')
        self.version_file = '.version'
        
    def run_command(self, cmd):
        """Esegue comando e ritorna output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)

    def get_next_version(self):
        """Ottiene la prossima versione"""
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    current = f.read().strip()
                    # Formato: v1.0.0
                    match = re.match(r'v(\d+)\.(\d+)\.(\d+)', current)
                    if match:
                        major, minor, patch = map(int, match.groups())
                        return f"v{major}.{minor}.{patch + 1}"
            except:
                pass
        return "v1.0.0"

    def save_version(self, version):
        """Salva la versione corrente"""
        with open(self.version_file, 'w') as f:
            f.write(version)

    def create_github_repo(self):
        """Crea repository su GitHub usando API"""
        if not self.token:
            print("⚠️  Token GitHub non trovato. Provo a creare con git...")
            return False

        import requests

        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }

        data = {
            'name': self.project_name,
            'description': f'Auto-created repository for {self.project_name}',
            'private': False
        }

        try:
            response = requests.post(
                'https://api.github.com/user/repos',
                headers=headers,
                json=data
            )
            return response.status_code == 201
        except Exception as e:
            print(f"⚠️  Errore API GitHub: {e}")
            return False

    def repo_exists(self):
        """Controlla se il repository esiste"""
        repo_url = f"https://github.com/{self.username}/{self.project_name}.git"
        success, _, _ = self.run_command(f"git ls-remote {repo_url}")
        return success
    
    def save_project(self, commit_message=None):
        """Salva progetto su GitHub con versioning automatico"""
        print(f"🚀 Salvando '{self.project_name}' su GitHub...")

        # Init git se necessario
        if not os.path.exists('.git'):
            print("📁 Inizializzo repository...")
            self.run_command("git init")

        # Add files
        print("📝 Aggiungendo file...")
        self.run_command("git add .")

        # Genera versione automatica se non specificato messaggio
        if not commit_message:
            version = self.get_next_version()
            commit_message = f"{version}: Auto-save {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            self.save_version(version)
            # Aggiungi il file versione al commit
            self.run_command("git add .version")

        # Commit
        success, _, _ = self.run_command(f'git commit -m "{commit_message}"')
        if not success:
            print("ℹ️  Nessun cambiamento da committare")
            return

        # Setup remote
        repo_url = f"https://github.com/{self.username}/{self.project_name}.git"
        self.run_command(f"git remote remove origin 2>/dev/null")
        self.run_command(f"git remote add origin {repo_url}")

        # Controlla se repository esiste
        if not self.repo_exists():
            print("🔧 Repository non esiste, lo creo automaticamente...")

            # Prova a creare con API GitHub
            if self.create_github_repo():
                print("✅ Repository creato con API GitHub!")
            else:
                # Fallback: crea repository vuoto e prova push
                print("⚠️  Creazione con API fallita, provo con git...")
                # Crea un repository vuoto su GitHub manualmente
                self.create_repo_with_git()

        # Get current branch name
        success, current_branch, _ = self.run_command("git branch --show-current")
        if not success:
            # Fallback for older git versions
            success, branch_output, _ = self.run_command("git branch")
            current_branch = branch_output.replace("*", "").strip() if success else "master"
        else:
            current_branch = current_branch.strip()

        # Push
        print("⬆️  Caricando su GitHub...")
        success, _, error = self.run_command(f"git push -u origin {current_branch}")

        if success:
            print(f"✅ Progetto salvato: {repo_url}")
            print(f"📦 Versione: {commit_message.split(':')[0] if ':' in commit_message else 'N/A'}")
        else:
            print(f"❌ Errore: {error}")
            if "Repository not found" in error:
                print(f"\n💡 Impossibile creare automaticamente il repository!")
                print(f"   Crea manualmente: https://github.com/new")
                print(f"   Nome repository: {self.project_name}")
                print(f"   Poi rilancia questo script.")

    def create_repo_with_git(self):
        """Metodo alternativo per creare repository"""
        print("💡 Per creare automaticamente il repository:")
        print("   1. Installa GitHub CLI: winget install GitHub.cli")
        print("   2. Oppure crea manualmente su https://github.com/new")
        print(f"   3. Nome repository: {self.project_name}")

    def install_dependencies(self):
        """Installa dipendenze necessarie"""
        try:
            import requests
            return True
        except ImportError:
            print("📦 Installando dipendenze...")
            success, _, _ = self.run_command("pip install requests")
            if success:
                print("✅ Dipendenze installate!")
                return True
            else:
                print("❌ Errore installazione dipendenze")
                return False

if __name__ == "__main__":
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    saver = GitHubSaver()

    # Installa dipendenze se necessario
    saver.install_dependencies()

    saver.save_project(message)
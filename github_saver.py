#!/usr/bin/env python3
import os
import subprocess
import sys
from datetime import datetime

class GitHubSaver:
    def __init__(self, username="Cocozza-simone"):
        self.username = username or input("GitHub username: ")
        self.project_name = os.path.basename(os.getcwd())
        
    def run_command(self, cmd):
        """Esegue comando e ritorna output"""
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode == 0, result.stdout, result.stderr
        except Exception as e:
            return False, "", str(e)
    
    def save_project(self, commit_message=None):
        """Salva progetto su GitHub"""
        print(f"🚀 Salvando '{self.project_name}' su GitHub...")
        
        # Init git se necessario
        if not os.path.exists('.git'):
            print("📁 Inizializzo repository...")
            self.run_command("git init")
        
        # Add files
        print("📝 Aggiungendo file...")
        self.run_command("git add .")
        
        # Commit
        if not commit_message:
            commit_message = f"Auto-save: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        success, _, _ = self.run_command(f'git commit -m "{commit_message}"')
        if not success:
            print("ℹ️  Nessun cambiamento da committare")
        
        # Setup remote
        repo_url = f"https://github.com/{self.username}/{self.project_name}.git"
        self.run_command(f"git remote remove origin 2>/dev/null")
        self.run_command(f"git remote add origin {repo_url}")
        
        # Push
        print("⬆️  Caricando su GitHub...")
        success, _, error = self.run_command("git push -u origin main")
        if not success:
            success, _, _ = self.run_command("git push -u origin master")
        
        if success:
            print(f"✅ Progetto salvato: {repo_url}")
        else:
            print(f"❌ Errore: {error}")

if __name__ == "__main__":
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None
    saver = GitHubSaver()
    saver.save_project(message)
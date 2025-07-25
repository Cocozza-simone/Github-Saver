#!/usr/bin/env python3
"""
Test script per verificare le funzionalità interattive
"""
import os
import sys

# Aggiungi il percorso corrente per importare github_saver
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from github_saver import GitHubSaver

def test_interactive():
    print("🧪 TEST INTERATTIVO GITHUB SAVER")
    print("=" * 50)
    
    # Test con parametri predefiniti
    current_dir = os.getcwd()
    print(f"📁 Usando cartella corrente: {current_dir}")
    
    # Crea istanza con parametri predefiniti
    saver = GitHubSaver(project_path=current_dir)
    
    print(f"✅ Progetto rilevato: {saver.project_name}")
    print(f"✅ Username: {saver.username}")
    print(f"✅ Token presente: {'Sì' if saver.token else 'No'}")
    
    # Test messaggio di commit
    print("\n💬 Test messaggio di commit:")
    test_message = "Test: Verifica funzionalità interattive"
    print(f"✅ Messaggio di test: {test_message}")
    
    # Salva il progetto
    saver.save_project(commit_message=test_message)

if __name__ == "__main__":
    test_interactive()

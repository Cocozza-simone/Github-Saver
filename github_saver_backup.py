#!/usr/bin/env python3
import os
import subprocess
import sys
import re
from datetime import datetime
from typing import Optional, Tuple, List

# --- Dependency Check ---
try:
    import requests
except ImportError:
    print("Errore: La dipendenza 'requests' non è installata.", file=sys.stderr)
    print("Per favore, eseguì: pip install requests", file=sys.stderr)
    sys.exit(1)

class GitHubSaver:
    """
    A class to automate saving a project to a new or existing GitHub repository.
    It handles git initialization, versioning, repository creation, and pushing.
    """

<<<<<<< HEAD
    def __init__(self, username: str = "Cocozza-simone", token: Optional[str] = None, project_path: Optional[str] = None):
=======
    def __init__(self, username: str = "name-github", token: Optional[str] = None):
>>>>>>> 149e2d8ffa99c957ede634902da4e915dda4c11b
        """
        Initializes the GitHubSaver instance.

        Args:
            username (str): The GitHub username. Defaults to "name-github".
            token (Optional[str]): A GitHub Personal Access Token. If None, it will be
                                   loaded from environment variables or a .env file.
            project_path (Optional[str]): Path to the project directory. If None, will ask user.
        """
        self.username: str = username or input("Per favore, inserisci il tuo username GitHub: ")
        self.project_path: str = project_path or self._ask_project_path()
        self.project_name: str = os.path.basename(self.project_path).replace(" ", "-")
        self.token: Optional[str] = token or self._load_token()
        self.version_file: str = '.version'

    def _ask_project_path(self) -> str:
        """
        Chiede all'utente di specificare la cartella del progetto da salvare.

        Returns:
            str: Il percorso della cartella del progetto.
        """
        print("\n📁 SELEZIONE CARTELLA PROGETTO")
        print("=" * 50)

        current_dir = os.getcwd()
        print(f"📍 Cartella corrente: {current_dir}")

        # Mostra le cartelle disponibili nella directory corrente
        try:
            dirs = [d for d in os.listdir(current_dir)
                   if os.path.isdir(os.path.join(current_dir, d)) and not d.startswith('.')]
            if dirs:
                print("\n📂 Cartelle disponibili:")
                for i, dir_name in enumerate(dirs, 1):
                    print(f"   {i}. {dir_name}")
        except:
            dirs = []

        print("\n🎯 Opzioni:")
        print("   • Premi INVIO per usare la cartella corrente")
        print("   • Digita il numero della cartella dalla lista")
        print("   • Digita il percorso completo della cartella")

        while True:
            choice = input("\n👉 Scegli la cartella del progetto: ").strip()

            # Cartella corrente (default)
            if not choice:
                return current_dir

            # Numero dalla lista
            if choice.isdigit() and dirs:
                idx = int(choice) - 1
                if 0 <= idx < len(dirs):
                    selected_path = os.path.join(current_dir, dirs[idx])
                    print(f"✅ Selezionata: {selected_path}")
                    return selected_path
                else:
                    print(f"❌ Numero non valido. Scegli tra 1 e {len(dirs)}")
                    continue

            # Percorso personalizzato
            if os.path.isdir(choice):
                abs_path = os.path.abspath(choice)
                print(f"✅ Selezionata: {abs_path}")
                return abs_path
            else:
                print(f"❌ Cartella non trovata: {choice}")
                print("   Riprova con un percorso valido.")

    def _load_token(self) -> Optional[str]:
        """
        Loads the GitHub token from the 'GITHUB_TOKEN' environment variable
        or from a .env file in the current directory.

        Returns:
            Optional[str]: The GitHub token if found, otherwise None.
        """
        # 1. Try environment variable first (best practice)
        token = os.getenv('GITHUB_TOKEN')
        if token:
            return token

        # 2. Fallback to .env file
        env_path = os.path.join(os.getcwd(), '.env')
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        if line.strip().startswith('GITHUB_TOKEN='):
                            return line.split('=', 1)[1].strip()
            except IOError as e:
                print(f"⚠️  Impossibile leggere il file .env: {e}", file=sys.stderr)
        return None

    def _run_command(self, cmd: List[str]) -> Tuple[bool, str, str]:
        """
        Executes a shell command and returns its status and output.

        Args:
            cmd (List[str]): The command to execute as a list of arguments.

        Returns:
            Tuple[bool, str, str]: A tuple containing success (bool),
                                   stdout (str), and stderr (str).
        """
        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=False
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except FileNotFoundError as e:
            return False, "", f"Comando non trovato: {e}"
        except Exception as e:
            return False, "", str(e)

    def _get_next_version(self) -> str:
        """
        Calculates the next semantic version (vX.Y.Z) based on the .version file.
        Increments the patch number. If the file doesn't exist or is invalid,
        it starts from "v1.0.0".

        Returns:
            str: The next version string (e.g., "v1.0.1").
        """
        if os.path.exists(self.version_file):
            try:
                with open(self.version_file, 'r') as f:
                    current_version = f.read().strip()
                match = re.match(r'v(\d+)\.(\d+)\.(\d+)', current_version)
                if match:
                    major, minor, patch = map(int, match.groups())
                    return f"v{major}.{minor}.{patch + 1}"
            except (IOError, ValueError) as e:
                print(f"⚠️  Impossibile leggere o interpretare il file di versione: {e}. Ricomincio da v1.0.0.", file=sys.stderr)
        return "v1.0.0"

    def _save_version(self, version: str) -> None:
        """Saves the current version string to the .version file."""
        try:
            with open(self.version_file, 'w') as f:
                f.write(version)
        except IOError as e:
            print(f"❌ Errore nel salvataggio del file di versione: {e}", file=sys.stderr)

    def _repo_exists_on_github(self) -> bool:
        """Checks if the remote repository already exists on GitHub."""
        repo_url = f"https://github.com/{self.username}/{self.project_name}.git"
        success, _, _ = self._run_command(["git", "ls-remote", repo_url])
        return success

    def _create_repo_with_gh_cli(self) -> bool:
        """
        Tries to create a GitHub repository using the GitHub CLI ('gh').
        This is the preferred method for automatic creation if available.

        Returns:
            bool: True if the repository was created successfully, False otherwise.
        """
        success, _, _ = self._run_command(["gh", "--version"])
        if not success:
            return False

        print("🔧 Tentativo di creare il repository con la GitHub CLI...")
        # Creates the repo, sets the remote, and pushes the current branch
        success, stdout, stderr = self._run_command([
            "gh", "repo", "create", self.project_name,
            "--public", "--source=.", "--remote=origin", "--push"
        ])

        if success:
            print("✅ Repository creato e codice caricato con successo tramite GitHub CLI!")
            return True
        else:
            # Handle case where repo already exists on GitHub but not locally
            if "already exists" in stderr:
                print("ℹ️  Il repository esiste già su GitHub. Configuro il remote e procedo con il push.")
                return False # Let the main logic handle the push
            print(f"❌ Errore durante la creazione con GitHub CLI:\n{stderr}", file=sys.stderr)
            return False

    def _create_repo_with_api(self) -> bool:
        """
        Creates a GitHub repository using the GitHub REST API as a fallback.

        Returns:
            bool: True if creation was successful, False otherwise.
        """
        if not self.token:
            print("⚠️  Token GitHub non trovato. Impossibile usare l'API.", file=sys.stderr)
            return False

        print("🔧 Token trovato. Tentativo di creare il repository con l'API GitHub...")
        headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        data = {
            'name': self.project_name,
            'description': f'Auto-created repository for {self.project_name}',
            'private': False
        }
        api_url = 'https://api.github.com/user/repos'

        try:
            response = requests.post(api_url, headers=headers, json=data)
            if response.status_code == 201:
                print("✅ Repository creato con successo tramite API!")
                return True
            else:
                error_details = response.json().get('message', 'Nessun dettaglio')
                print(f"❌ Fallita la creazione del repository via API (Status: {response.status_code}): {error_details}", file=sys.stderr)
                return False
        except requests.RequestException as e:
            print(f"❌ Errore di rete durante la chiamata API GitHub: {e}", file=sys.stderr)
            return False

    def _ask_commit_message(self) -> str:
        """
        Chiede all'utente di inserire un messaggio di commit.

        Returns:
            str: Il messaggio di commit scelto dall'utente.
        """
        print("\n💬 MESSAGGIO DI COMMIT")
        print("=" * 50)

        # Mostra la versione corrente
        current_version = self._get_next_version()
        print(f"📦 Prossima versione: {current_version}")

        print("\n🎯 Opzioni:")
        print("   • Premi INVIO per commit automatico con versione")
        print("   • Digita un messaggio personalizzato")

        message = input("\n👉 Inserisci il messaggio di commit: ").strip()

        if not message:
            # Messaggio automatico con versione
            auto_message = f"feat: Auto-save version {current_version}"
            print(f"✅ Messaggio automatico: {auto_message}")
            return auto_message
        else:
            print(f"✅ Messaggio personalizzato: {message}")
            return message

    def save_project(self, commit_message: Optional[str] = None) -> None:
        """
        Main method to orchestrate the entire process of saving the project.

        Args:
            commit_message (Optional[str]): A custom commit message. If None, will ask user.
        """
        # Cambia nella directory del progetto
        original_dir = os.getcwd()
        os.chdir(self.project_path)

        try:
            print(f"🚀 Inizio il salvataggio del progetto '{self.project_name}' su GitHub...")
            print(f"📁 Cartella progetto: {self.project_path}")

            # Chiedi il messaggio di commit se non fornito
            if not commit_message:
                commit_message = self._ask_commit_message()

            # 1. Initialize Git if needed
            if not os.path.exists('.git'):
                print("📁 Repository Git non trovato. Lo inizializzo...")
                self._run_command(["git", "init"])

            # 2. Add all files
            print("📝 Aggiungo tutti i file all'area di staging...")
            self._run_command(["git", "add", "."])

            # 3. Create commit message and version (se automatico)
            if "Auto-save version" in commit_message:
                version = self._get_next_version()
                commit_message = f"feat: Auto-save version {version}"
                self._save_version(version)
                self._run_command(["git", "add", self.version_file])

            # 4. Commit changes
            print(f"💬 Eseguo il commit con il messaggio: \"{commit_message}\"")
            success, _, _ = self._run_command(["git", "commit", "-m", commit_message])
            if not success:
                print("ℹ️  Nessun cambiamento da salvare. Il progetto è già aggiornato.")
                return

            # 5. Check for remote repository and create if it doesn't exist
            repo_url = f"https://github.com/{self.username}/{self.project_name}.git"
            if not self._repo_exists_on_github():
                print(f"🔧 Il repository '{self.project_name}' non esiste su GitHub.")
                # Try GitHub CLI first
                if self._create_repo_with_gh_cli():
                    # gh cli already pushed, so the job is done
                    print(f"✅ Progetto salvato con successo: {repo_url}")
                    return
                # Fallback to API
                elif not self._create_repo_with_api():
                    print("\n❌ Creazione automatica del repository fallita.", file=sys.stderr)
                    print("💡 Per favore, crea il repository manualmente su GitHub:", file=sys.stderr)
                    print(f"   1. Vai su: https://github.com/new", file=sys.stderr)
                    print(f"   2. Usa come nome: {self.project_name}", file=sys.stderr)
                    print("   3. Rilancia questo script per effettuare il push.", file=sys.stderr)
                    return

            # 6. Set remote and push
            self._run_command(["git", "remote", "set-url", "origin", repo_url])

            # Get current branch name
            success, branch, _ = self._run_command(["git", "branch", "--show-current"])
            if not success:
                branch = "main" # Default to main if command fails

            print(f"⬆️  Carico le modifiche sul branch '{branch}'...")
            success, stdout, stderr = self._run_command(["git", "push", "-u", "origin", branch])

            # Se il push fallisce per conflitti, prova a fare pull e ripush
            if not success and ("fetch first" in stderr or "rejected" in stderr):
                print("🔄 Rilevati cambiamenti remoti, sincronizzazione in corso...")

                # Prova a fare pull con rebase
                pull_success, _, pull_error = self._run_command(["git", "pull", "--rebase", "origin", branch])

                if pull_success:
                    print("✅ Sincronizzazione completata, riprovo il push...")
                    success, stdout, stderr = self._run_command(["git", "push", "-u", "origin", branch])
                else:
                    print(f"⚠️  Errore durante la sincronizzazione: {pull_error}")
                    print("💡 Provo con merge invece di rebase...")

                    # Fallback: prova con merge normale
                    merge_success, _, merge_error = self._run_command(["git", "pull", "origin", branch])
                    if merge_success:
                        print("✅ Merge completato, riprovo il push...")
                        success, stdout, stderr = self._run_command(["git", "push", "-u", "origin", branch])

            if success:
                version_tag = commit_message.split()[-1] if 'version' in commit_message else 'N/A'
                print("\n🎉🎉🎉")
                print(f"✅ Progetto salvato con successo: {repo_url}")
                print(f"📦 Versione committata: {version_tag}")
                print("🎉🎉🎉\n")
            else:
                print(f"\n❌ Errore durante il push su GitHub:\n{stderr}", file=sys.stderr)
                print("\n💡 Suggerimenti per risolvere:")
                print("   1. Controlla la connessione internet")
                print("   2. Verifica i permessi del repository")
                print("   3. Prova a fare 'git pull' manualmente")

        finally:
            # Torna alla directory originale
            os.chdir(original_dir)

def main():
    """Main function to run the script."""
    print("🎯 GITHUB SAVER - Salvataggio Automatico Progetti")
    print("=" * 60)

    # Get commit message from command-line arguments, if any
    message = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else None

    # Crea l'istanza (chiederà cartella e altri dettagli)
    saver = GitHubSaver()

    # Salva il progetto (chiederà il messaggio se non fornito)
    saver.save_project(commit_message=message)

if __name__ == "__main__":
    main()

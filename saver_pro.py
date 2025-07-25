#!/usr/bin/env python3
"""
GitHub Saver Pro - Enhanced automatic project saving to GitHub
Advanced features: Smart commit types, file analysis, backup system, and more!
"""

import os
import subprocess
import sys
import re
import json
import shutil
import time
from datetime import datetime
from typing import Optional, Tuple, List, Dict, Set
from pathlib import Path
import hashlib
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import asyncio
import select

# --- Dependency Check ---
REQUIRED_PACKAGES = ['requests', 'colorama', 'rich']
missing_packages = []

for package in REQUIRED_PACKAGES:
    try:
        __import__(package)
    except ImportError:
        missing_packages.append(package)

if missing_packages:
    print("❌ Dipendenze mancanti:", ', '.join(missing_packages))
    print(f"📦 Installa con: pip install {' '.join(missing_packages)}")
    sys.exit(1)

import requests
from colorama import init, Fore, Style
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.syntax import Syntax

# Initialize colorama and rich
init(autoreset=True)
console = Console()

class SmartConfirm:
    """Smart confirmation class with timeout support."""
    @staticmethod
    def ask(prompt: str, default: bool = True) -> bool:
        return timeout_input(prompt, timeout=5, default=default)

def timeout_input(prompt: str, timeout: int = 5, default: bool = True) -> bool:
    """Input with timeout that returns default value if no input is received."""
    import msvcrt
    import time
    
    console.print(f"{prompt} (auto-{default} in {timeout}s)")
    
    start_time = time.time()
    input_str = ''
    
    while True:
        if msvcrt.kbhit():
            char = msvcrt.getwche()
            if char == '\r':  # Enter key
                break
            input_str += char
        
        if time.time() - start_time > timeout:
            console.print(f"\n⏱️ No input received, using default: {'Yes' if default else 'No'}")
            return default
            
        time.sleep(0.1)
    
    return input_str.lower() in ['y', 'yes', '']

class ProjectAnalyzer:
    """Analyzes project structure and suggests appropriate commit types."""
    
    def __init__(self, project_path: str):
        self.project_path = Path(project_path)
        self.file_queue = Queue()
        
    def _scan_files(self, pattern: str) -> List[Path]:
        """Scan files matching pattern in separate thread."""
        return list(self.project_path.rglob(pattern))
        
    def detect_project_type(self) -> str:
        """Detects the type of project based on files present using threads."""
        indicators = {
            'python': ['*.py', 'requirements.txt', 'setup.py', 'pyproject.toml'],
            'javascript': ['package.json', '*.js', '*.ts', 'yarn.lock'],
            'web': ['index.html', '*.css', '*.html'],
            'java': ['*.java', 'pom.xml', 'build.gradle'],
            'c++': ['*.cpp', '*.h', 'CMakeLists.txt', 'Makefile'],
            'rust': ['Cargo.toml', '*.rs'],
            'go': ['go.mod', '*.go'],
            'mobile': ['pubspec.yaml', '*.dart', '*.swift', '*.kt']
        }
        
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {}
            for project_type, patterns in indicators.items():
                for pattern in patterns:
                    future = executor.submit(self._scan_files, pattern)
                    futures[future] = project_type
                    
            for future in as_completed(futures):
                project_type = futures[future]
                if future.result():
                    return project_type
                    
        return 'generic'
    
    def get_changed_files(self) -> List[str]:
        """Gets list of changed files using git."""
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', 'HEAD'], 
                capture_output=True, text=True, cwd=self.project_path
            )
            if result.returncode == 0:
                return [f for f in result.stdout.strip().split('\n') if f]
        except:
            pass
        return []
    
    def suggest_commit_type(self) -> str:
        """Suggests appropriate commit type based on changes."""
        changed_files = self.get_changed_files()
        if not changed_files:
            return 'feat'
            
        # Analyze file types
        has_new_files = any('new file' in f for f in changed_files)
        has_docs = any(f.endswith(('.md', '.txt', '.rst')) for f in changed_files)
        has_tests = any('test' in f.lower() or f.endswith('_test.py') for f in changed_files)
        has_config = any(f.endswith(('.json', '.yaml', '.yml', '.toml', '.ini')) for f in changed_files)
        
        if has_new_files:
            return 'feat'
        elif has_tests:
            return 'test'
        elif has_docs:
            return 'docs'
        elif has_config:
            return 'config'
        else:
            return 'fix'

class BackupManager:
    """Manages local backups of projects with async operations."""
    
    def __init__(self, backup_dir: str = "~/.github_saver_backups"):
        self.backup_dir = Path(backup_dir).expanduser()
        self.backup_dir.mkdir(exist_ok=True)
        self.backup_queue = Queue()
        self._start_backup_worker()
        
    def _start_backup_worker(self):
        """Start background worker thread for backups."""
        self.backup_thread = threading.Thread(target=self._backup_worker, daemon=True)
        self.backup_thread.start()
        
    def _backup_worker(self):
        """Background worker that processes backup tasks."""
        while True:
            task = self.backup_queue.get()
            if task is None:
                break
            src, dest = task
            try:
                shutil.copytree(src, dest, ignore=shutil.ignore_patterns('.git'))
            except Exception as e:
                console.print(f"⚠️ Backup failed: {e}", style="yellow")
            self.backup_queue.task_done()

    async def create_backup(self, project_path: str, project_name: str) -> str:
        """Creates a timestamped backup of the project asynchronously."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{project_name}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        # Queue backup task
        self.backup_queue.put((project_path, backup_path))
        return str(backup_path)

    def cleanup_old_backups(self, project_name: str, max_backups: int = 5) -> None:
        """Clean up old backups keeping only the most recent ones.
        
        Args:
            project_name: Name of the project to cleanup backups for
            max_backups: Maximum number of backups to keep (default: 5)
        """
        # Get all backups for this project
        backups = sorted(
            [p for p in self.backup_dir.glob(f"{project_name}_*")],
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )

        # Keep only max_backups most recent backups
        if len(backups) > max_backups:
            with ThreadPoolExecutor(max_workers=4) as executor:
                # Delete old backups in parallel
                futures = []
                for backup in backups[max_backups:]:
                    futures.append(
                        executor.submit(shutil.rmtree, str(backup))
                    )
                
                # Wait for all deletions to complete
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        console.print(f"⚠️ Failed to delete old backup: {e}", style="yellow")
                        
            console.print(
                f"🧹 Cleaned up {len(backups) - max_backups} old backups", 
                style="green"
            )

class GitHubSaverPro:
    """Enhanced GitHub project saver with async/threading support."""

    COMMIT_TYPES = {
        'feat': 'New feature',
        'fix': 'Bug fix',
        'docs': 'Documentation',
        'style': 'Code style',
        'refactor': 'Code refactoring',
        'test': 'Tests',
        'chore': 'Maintenance',
        'perf': 'Performance',
        'ci': 'CI/CD',
        'build': 'Build system',
        'revert': 'Revert changes'
    }

    def __init__(self, username: str = "nome-github", token: Optional[str] = None, 
                 project_path: Optional[str] = None, config_file: str = "~/.github_saver_config.json"):
        """Initialize with enhanced configuration."""
        self.config_file = Path(config_file).expanduser()
        self.config = self._load_config()
        
        self.username = username or self.config.get('username') or self._ask_username()
        self.project_path = project_path or self._ask_project_path()
        self.project_name = Path(self.project_path).name.replace(" ", "-")
        self.token = token or self._load_token()
        
        self.analyzer = ProjectAnalyzer(self.project_path)
        self.backup_manager = BackupManager()
        
        # Enhanced version management
        self.version_file = Path(self.project_path) / '.version'
        self.changelog_file = Path(self.project_path) / 'CHANGELOG.md'
        
        self.thread_pool = ThreadPoolExecutor(max_workers=4)
        
    def _load_config(self) -> Dict:
        """Load configuration from JSON file."""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def _save_config(self):
        """Save current configuration."""
        config = {
            'username': self.username,
            'last_project': self.project_path,
            'backup_enabled': getattr(self, 'backup_enabled', True)
        }
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            console.print(f"⚠️ Could not save config: {e}", style="yellow")

    def _ask_username(self) -> str:
        """Ask for GitHub username with validation."""
        return Prompt.ask("🧑‍💻 GitHub username", default="nome-github")

    def _ask_project_path(self) -> str:
        """Automatic project path selection - uses current directory."""
        current_dir = Path.cwd()
        console.print(f"📍 Using current directory: [cyan]{current_dir}[/cyan]")
        return str(current_dir)

    def _load_token(self) -> Optional[str]:
        """Enhanced token loading with multiple sources."""
        sources = [
            ('Environment Variable', lambda: os.getenv('GITHUB_TOKEN')),
            ('.env file', self._load_from_env_file),
            ('Config file', lambda: self.config.get('token')),
            ('Git credential', self._load_from_git_credential)
        ]
        
        for source_name, loader in sources:
            try:
                token = loader()
                if token:
                    console.print(f"🔑 Token loaded from: {source_name}", style="green")
                    return token
            except:
                continue
        
        console.print("⚠️ No GitHub token found! Please set GITHUB_TOKEN environment variable or create .env file", style="yellow")
        return None

    def _load_from_env_file(self) -> Optional[str]:
        """Load token from .env file."""
        env_path = Path.cwd() / '.env'
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip().startswith('GITHUB_TOKEN='):
                            return line.split('=', 1)[1].strip()
            except UnicodeDecodeError:
                with open(env_path, 'r', encoding='latin-1') as f:
                    for line in f:
                        if line.strip().startswith('GITHUB_TOKEN='):
                            return line.split('=', 1)[1].strip()
        return None  # Fixed indentation

    def _load_from_git_credential(self) -> Optional[str]:
        """Try to extract token from git credentials."""
        try:
            result = subprocess.run(
                ['git', 'config', '--global', 'github.token'],
                capture_output=True, text=True
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None

    def _run_command(self, cmd: List[str], cwd: Optional[str] = None) -> Tuple[bool, str, str]:
        """Enhanced command execution with better error handling."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=False,
                cwd=cwd or self.project_path,
                encoding='utf-8',
                errors='replace'  # Replace problematic characters
            )
            return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
        except FileNotFoundError as e:
            return False, "", f"Command not found: {e}"
        except UnicodeDecodeError as e:
            # Fallback to latin-1 encoding
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    check=False,
                    cwd=cwd or self.project_path,
                    encoding='latin-1'
                )
                return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
            except:
                return False, "", f"Encoding error: {e}"
        except Exception as e:
            return False, "", str(e)

    def _get_next_version(self, version_type: str = 'patch') -> str:
        """Enhanced version management with semantic versioning."""
        current = "v0.0.0"
        
        if self.version_file.exists():
            try:
                current = self.version_file.read_text().strip()
            except:
                pass
        
        match = re.match(r'v(\d+)\.(\d+)\.(\d+)', current)
        if not match:
            return "v1.0.0"
            
        major, minor, patch = map(int, match.groups())
        
        if version_type == 'major':
            return f"v{major + 1}.0.0"
        elif version_type == 'minor':
            return f"v{major}.{minor + 1}.0"
        else:  # patch
            return f"v{major}.{minor}.{patch + 1}"

    def _create_changelog_entry(self, version: str, commit_message: str, commit_type: str):
        """Create or update CHANGELOG.md."""
        date_str = datetime.now().strftime("%Y-%m-%d")
        entry = f"\n## {version} - {date_str}\n\n### {self.COMMIT_TYPES.get(commit_type, 'Changes')}\n- {commit_message}\n"
        
        if self.changelog_file.exists():
            content = self.changelog_file.read_text()
            # Insert after the first line (title)
            lines = content.split('\n')
            lines.insert(1, entry)
            self.changelog_file.write_text('\n'.join(lines))
        else:
            self.changelog_file.write_text(f"# Changelog\n{entry}")

    def _smart_commit_message(self) -> Tuple[str, str]:
        """Automatic commit message builder with smart suggestions."""
        # Analyze project and suggest commit type
        suggested_type = self.analyzer.suggest_commit_type()
        project_type = self.analyzer.detect_project_type()

        console.print(f"🔍 Detected project type: [green]{project_type}[/green]")
        console.print(f"🎯 Using commit type: [yellow]{suggested_type}[/yellow]")

        # Generate automatic commit message based on changes
        changed_files = self.analyzer.get_changed_files()
        if changed_files:
            if len(changed_files) == 1:
                message = f"Update {Path(changed_files[0]).name}"
            elif len(changed_files) <= 3:
                files = ", ".join([Path(f).name for f in changed_files[:3]])
                message = f"Update {files}"
            else:
                message = f"Update {len(changed_files)} files"
        else:
            message = "Auto-save project changes"

        # Build full commit message
        full_message = f"{suggested_type}: {message}"

        console.print(f"💬 Commit message: [cyan]{full_message}[/cyan]")
        return full_message, suggested_type

    def _safe_commit_message(self, commit_type: str, emoji: str, message: str) -> str:
        """Create a commit message that handles encoding issues gracefully."""
        # For Windows systems with encoding issues, skip emojis entirely
        if os.name == 'nt' and (sys.stdout.encoding or '').lower() in ['cp1252', 'charmap']:
            return f"{commit_type}: {message}"

        try:
            # Try with emoji first
            full_message = f"{commit_type}: {emoji} {message}"
            # Test if it can be encoded
            full_message.encode('utf-8')
            return full_message
        except (UnicodeEncodeError, LookupError):
            # Fallback without emoji
            return f"{commit_type}: {message}"

    def _show_project_stats(self):
        """Display project statistics."""
        stats = {
            "Total files": len(list(Path(self.project_path).rglob('*'))),
            "Python files": len(list(Path(self.project_path).rglob('*.py'))),
            "Git commits": self._get_commit_count(),
            "Project size": self._get_project_size(),
            "Last modified": self._get_last_modified()
        }
        
        table = Table(title=f"📊 Project Stats: {self.project_name}")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")
        
        for metric, value in stats.items():
            table.add_row(metric, str(value))
        
        console.print(table)

    def _get_commit_count(self) -> int:
        """Get number of commits in repository."""
        success, output, _ = self._run_command(['git', 'rev-list', '--count', 'HEAD'])
        return int(output) if success and output.isdigit() else 0

    def _get_project_size(self) -> str:
        """Get human-readable project size."""
        total_size = sum(f.stat().st_size for f in Path(self.project_path).rglob('*') if f.is_file())
        for unit in ['B', 'KB', 'MB', 'GB']:
            if total_size < 1024:
                return f"{total_size:.1f} {unit}"
            total_size /= 1024
        return f"{total_size:.1f} TB"

    def _get_last_modified(self) -> str:
        """Get last modification time."""
        try:
            latest = max(Path(self.project_path).rglob('*'), key=lambda f: f.stat().st_mtime if f.is_file() else 0)
            return datetime.fromtimestamp(latest.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        except:
            return "Unknown"

    def _interactive_file_selector(self) -> List[str]:
        """Allow user to select which files to commit."""
        success, output, _ = self._run_command(['git', 'status', '--porcelain'])
        if not success or not output:
            return []
        
        files = []
        for line in output.split('\n'):
            if line.strip():
                status = line[:2]
                filename = line[3:]
                files.append((status, filename))
        
        if not files:
            return []
        
        console.print("\n📋 [bold blue]FILES TO COMMIT[/bold blue]")
        
        table = Table()
        table.add_column("Status", style="yellow")
        table.add_column("File", style="cyan")
        table.add_column("Include", style="green")
        
        selected_files = []
        for status, filename in files:
            include = SmartConfirm.ask(f"Include {filename}?", default=True)  # Modified
            table.add_row(status, filename, "✅" if include else "❌")
            if include:
                selected_files.append(filename)
        
        console.print(table)
        return selected_files

    async def _parallel_git_operations(self, commands: List[List[str]]) -> List[Tuple[bool, str, str]]:
        """Execute multiple git commands in parallel."""
        loop = asyncio.get_event_loop()
        futures = []
        
        for cmd in commands:
            futures.append(loop.run_in_executor(
                self.thread_pool, 
                self._run_command,
                cmd
            ))
            
        return await asyncio.gather(*futures)

    def _check_git_available(self) -> bool:
        """Check if git is available in the system."""
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                encoding='utf-8'
            )
            return result.returncode == 0
        except:
            return False

    async def save_project(self, commit_message: Optional[str] = None,
                    interactive: bool = False, backup: bool = True) -> None:
        """Enhanced async main method with parallel operations."""
        if not self._check_git_available():
            console.print("❌ Git is not available in the system", style="red")
            return
        
        try:
            with console.status("[bold green]Initializing GitHub Saver Pro...") as status:
                os.chdir(self.project_path)
                
                # Parallel initialization tasks
                init_tasks = [
                    self._show_project_stats() if interactive else None,
                    self.backup_manager.create_backup(self.project_path, self.project_name) if backup else None,
                ]
                
                await asyncio.gather(*[t for t in init_tasks if t is not None])
                
                # Parallel git operations
                if not Path('.git').exists():
                    status.update("[blue]Initializing Git repository...")
                    await self._parallel_git_operations([
                        ['git', 'init'],
                        ['git', 'add', '.']
                    ])
                
                # Always add all files automatically
                status.update("[blue]Adding all files...")
                self._run_command(['git', 'add', '.'])
                
                # Get commit message
                if not commit_message:
                    commit_message, commit_type = self._smart_commit_message()
                else:
                    commit_type = commit_message.split(':')[0] if ':' in commit_message else 'feat'
                
                # Handle versioning
                if 'version' in commit_message.lower() or not interactive:
                    version_type = 'patch'
                    if 'major' in commit_message.lower():
                        version_type = 'major'
                    elif 'minor' in commit_message.lower():
                        version_type = 'minor'
                    
                    version = self._get_next_version(version_type)
                    self.version_file.write_text(version)
                    self._create_changelog_entry(version, commit_message, commit_type)
                    self._run_command(['git', 'add', str(self.version_file)])
                    self._run_command(['git', 'add', str(self.changelog_file)])
                    
                    console.print(f"📦 Version updated to: [green]{version}[/green]")
                
                # Commit changes
                status.update("[blue]Creating commit...")
                success, output, error = self._run_command(['git', 'commit', '-m', commit_message])

                # Check for "nothing to commit" in both output and error
                nothing_to_commit = (
                    "nothing to commit" in (output or "").lower() or
                    "nothing to commit" in (error or "").lower()
                )

                if nothing_to_commit:
                    console.print("ℹ️ No changes to commit", style="yellow")
                    return
                elif not success:
                    console.print(f"❌ Commit failed: {error or 'Unknown error'}", style="red")
                    return
                
                # Check and create repository
                repo_url = f"https://github.com/{self.username}/{self.project_name}.git"
                
                if not self._repo_exists_on_github():
                    status.update("[yellow]Creating GitHub repository...")
                    if not (self._create_repo_with_gh_cli() or self._create_repo_with_api()):
                        console.print("❌ Failed to create repository", style="red")
                        self._show_manual_instructions()
                        return
                
                # Push to GitHub
                status.update("[blue]Pushing to GitHub...")
                self._setup_remote_and_push(repo_url)
            
            # Success message
            panel = Panel(
                f"🎉 [bold green]SUCCESS![/bold green]\n\n"
                f"📦 Project: [cyan]{self.project_name}[/cyan]\n"
                f"🔗 URL: [blue]{repo_url}[/blue]\n"
                f"💬 Commit: [yellow]{commit_message}[/yellow]",
                title="GitHub Saver Pro",
                border_style="green"
            )
            console.print(panel)
            
            # Save configuration
            self._save_config()
            
            # Cleanup old backups
            if backup:
                self.backup_manager.cleanup_old_backups(self.project_name)

        except Exception as e:
            console.print(f"❌ Error during save: {str(e)}", style="red")
            raise

    def _repo_exists_on_github(self) -> bool:
        """Check if repository exists on GitHub."""
        repo_url = f"https://github.com/{self.username}/{self.project_name}.git"
        success, _, _ = self._run_command(['git', 'ls-remote', repo_url])
        return success

    def _create_repo_with_gh_cli(self) -> bool:
        """Create repository using GitHub CLI."""
        success, _, _ = self._run_command(['gh', '--version'])
        if not success:
            return False
        
        console.print("🔧 Creating repository with GitHub CLI...", style="blue")
        success, _, error = self._run_command([
            'gh', 'repo', 'create', self.project_name,
            '--public', '--source=.', '--remote=origin', '--push'
        ])
        
        if success:
            console.print("✅ Repository created with GitHub CLI!", style="green")
            return True
        elif "already exists" in error:
            console.print("ℹ️ Repository already exists", style="yellow")
            return False
        else:
            console.print(f"❌ GitHub CLI failed: {error}", style="red")
            return False

    def _create_repo_with_api(self) -> bool:
        """Create repository using GitHub API."""
        if not self.token:
            console.print("⚠️ No GitHub token available", style="yellow")
            return False
        
        console.print("🔧 Creating repository with GitHub API...", style="blue")
        
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
                headers=headers, json=data, timeout=30
            )
            
            if response.status_code == 201:
                console.print("✅ Repository created with API!", style="green")
                return True
            else:
                error = response.json().get('message', 'Unknown error')
                console.print(f"❌ API failed ({response.status_code}): {error}", style="red")
                return False
                
        except requests.RequestException as e:
            console.print(f"❌ Network error: {e}", style="red")
            return False

    def _setup_remote_and_push(self, repo_url: str):
        """Setup remote and push changes."""
        # Check if origin remote exists, if not add it, otherwise set its URL
        success, _, _ = self._run_command(['git', 'remote', 'get-url', 'origin'])
        if not success:
            # Origin doesn't exist, add it
            self._run_command(['git', 'remote', 'add', 'origin', repo_url])
        else:
            # Origin exists, update its URL
            self._run_command(['git', 'remote', 'set-url', 'origin', repo_url])
        
        # Get current branch
        success, branch, _ = self._run_command(['git', 'branch', '--show-current'])
        branch = branch if success else 'main'
        
        # Push with progress
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task(f"Pushing to {branch}...", total=None)
            
            success, _, error = self._run_command(['git', 'push', '-u', 'origin', branch])
            
            if not success and ("fetch first" in error or "rejected" in error):
                progress.update(task, description="Syncing with remote...")
                
                # Try rebase
                pull_success, _, _ = self._run_command(['git', 'pull', '--rebase', 'origin', branch])
                if pull_success:
                    progress.update(task, description="Retrying push...")
                    success, _, error = self._run_command(['git', 'push', '-u', 'origin', branch])
            
            progress.remove_task(task)
        
        if not success:
            console.print(f"❌ Push failed: {error}", style="red")
            raise Exception(f"Push failed: {error}")

    def _show_manual_instructions(self):
        """Show manual repository creation instructions."""
        panel = Panel(
            f"Please create the repository manually:\n\n"
            f"1. Go to: [blue]https://github.com/new[/blue]\n"
            f"2. Repository name: [cyan]{self.project_name}[/cyan]\n"
            f"3. Make it public\n"
            f"4. Don't initialize with README\n"
            f"5. Run this script again",
            title="Manual Setup Required",
            border_style="yellow"
        )
        console.print(panel)

def main():
    """Enhanced async main function."""
    async def async_main():
        console.print(Panel(
            "[bold blue]GitHub Saver Pro[/bold blue]\n"
            "Enhanced automatic project saving to GitHub\n"
            "Smart commits • Analytics • Backups • Interactive",
            border_style="blue"
        ))
        
        # Parse command line arguments
        import argparse
        parser = argparse.ArgumentParser(description='GitHub Saver Pro')
        parser.add_argument('message', nargs='*', help='Commit message')
        parser.add_argument('--no-interactive', action='store_true', help='Disable interactive mode')
        parser.add_argument('--no-backup', action='store_true', help='Skip backup creation')
        parser.add_argument('--username', help='GitHub username')
        parser.add_argument('--project', help='Project path')
        
        args = parser.parse_args()
        
        try:
            saver = GitHubSaverPro(
                username=args.username,
                project_path=args.project
            )
            
            commit_message = ' '.join(args.message) if args.message else None
            
            await saver.save_project(
                commit_message=commit_message,
                interactive=not args.no_interactive,
                backup=not args.no_backup
            )

        except KeyboardInterrupt:
            console.print("\n👋 Operation cancelled", style="yellow")
        except Exception as e:
            console.print(f"\n❌ Error: {e}", style="red")
            sys.exit(1)

    asyncio.run(async_main())

if __name__ == "__main__":
    main()

import logging
import subprocess
from pathlib import Path
from typing import List, Dict

# Configure basic logging to log to the console
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

class ProjectBootstrapper:
    """
    Automates the initialization of a modern AI engineering Python project.
    Handles directory scaffolding, generating configuration files, and Git setup.
    """

    def __init__(self, base_path: str = ".") -> None:
        """
        Initializes the bootstrapper.

        Args:
            base_path (str): The root directory for the new project.
        """
        # Resolve to an absolute path for safety
        self.base_path: Path = Path(base_path).resolve()

    def create_directories(self, directories: List[str]) -> None:
        """
        Creates the standard project directory structure.

        Args:
            directories (List[str]): List of directory paths to create relative to base_path.
        """
        logging.info("Creating directory structure...")
        for dir_name in directories:
            dir_path: Path = self.base_path / dir_name
            
            # parents=True creates intermediate directories if needed
            # exist_ok=True prevents errors if the directory already exists
            dir_path.mkdir(parents=True, exist_ok=True)
            
            # Create an empty .gitkeep to ensure Git tracks these empty directories initially
            (dir_path / ".gitkeep").touch(exist_ok=True)
            logging.info(f"Created directory: {dir_name}/")

    def generate_files(self, files: Dict[str, str]) -> None:
        """
        Generates standard project configuration files with provided content.

        Args:
            files (Dict[str, str]): Dictionary mapping relative file paths to their string content.
        """
        logging.info("Generating configuration files...")
        
        # Ensure the base path itself exists before writing files to it
        self.base_path.mkdir(parents=True, exist_ok=True)
        
        for file_name, content in files.items():
            file_path: Path = self.base_path / file_name
            # Write the content to the file using standard UTF-8 encoding
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content.strip() + "\n")
            logging.info(f"Generated file: {file_name}")

    def initialize_git(self) -> bool:
        """
        Initializes a Git repository and creates the initial commit.

        Returns:
            bool: True if Git initialization was successful, False otherwise.
        """
        logging.info("Initializing Git repository...")
        try:
            # 1. Run 'git init' to create the repository (safe if already exists)
            subprocess.run(["git", "init"], cwd=self.base_path, check=True, capture_output=True)
            
            # 2. Stage all newly created directories and files
            subprocess.run(["git", "add", "."], cwd=self.base_path, check=True, capture_output=True)
            
            # 3. Create the first commit (or subsequent commit if changes exist)
            status = subprocess.run(["git", "status", "--porcelain"], cwd=self.base_path, check=True, capture_output=True)
            if status.stdout:
                commit_msg = "chore: Project setup (folders, configs, cursorrules)"
                subprocess.run(
                    ["git", "commit", "-m", commit_msg],
                    cwd=self.base_path, check=True, capture_output=True
                )
                logging.info("Git commit created.")
            else:
                logging.info("No new changes to commit in Git.")
                
            return True
            
        except subprocess.CalledProcessError as e:
            # Triggered if any git command returns a non-zero exit status
            error_msg = e.stderr.decode().strip() if e.stderr else str(e)
            logging.error(f"Git command failed: {error_msg}")
            return False
            
        except FileNotFoundError:
            # Triggered if the 'git' executable isn't found in the system PATH
            logging.error("Git executable not found. Ensure Git is installed.")
            return False

def main() -> None:
    """
    Runnable demo block to bootstrap an AI development environment.
    """
    print("--- Starting AI Project Initialization ---\n")
    
    # Target the current workspace
    target_project_dir: str = "."
    bootstrapper: ProjectBootstrapper = ProjectBootstrapper(base_path=target_project_dir)
    
    # Define the target folder structure for a standard AI application
    target_folders: List[str] = [
        "src",         # Core application code
        "tests",       # Unit and integration tests
        "docs",        # Documentation (Sphinx, MkDocs, etc.)
        "notebooks"    # Jupyter notebooks for EDA and prototyping
    ]
    
    # Define essential configuration files and their boilerplate contents
    config_files: Dict[str, str] = {
        "pyproject.toml": """
[build-system]
requires = ["setuptools>=61.0"]
build-backend = "setuptools.build_meta"

[project]
name = "nexus-forge"
version = "0.1.0"
description = "A standard AI engineering project setup in nexus-forge."
authors = [{name = "Your Name", email = "your.email@example.com"}]
requires-python = ">=3.9"
dependencies = [
    "numpy",
    "pandas",
    "scikit-learn"
]
        """,
        ".cursorrules": """
# Cursor Composer / AI Pair Programmer Context Rules
# 1. Always use Python 3.9+ syntax and include full type hints.
# 2. Write Google-style docstrings for all functions and classes.
# 3. Follow PEP 8 style guidelines implicitly.
# 4. Place application logic strictly in `src/` and all tests in `tests/`.
# 5. Prioritize writing modular, pure functions whenever possible to simplify testing.
        """,
        ".gitignore": """
# Python artifacts
__pycache__/
*.py[cod]
*$py.class
*.so

# Environments
.env
.venv
env/
venv/

# Jupyter
.ipynb_checkpoints

# AI Editor tools context (Optional to ignore, but good practice if local)
.cursor/
        """
    }

    # Execute the scaffolding workflow
    bootstrapper.create_directories(target_folders)
    bootstrapper.generate_files(config_files)
    
    # Initialize Git tracking for the newly generated project
    success: bool = bootstrapper.initialize_git()
    
    if success:
        print("\n--- Project initialization complete! ---")
        print(f"Your project is ready in: {Path(target_project_dir).resolve()}")
    else:
        print("\n--- Project initialization completed with warnings (Git failed). ---")

if __name__ == "__main__":
    main()

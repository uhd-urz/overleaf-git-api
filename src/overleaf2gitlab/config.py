import configparser
import os
from pathlib import Path

def read_config(file_path: str, verbose: bool) -> configparser.ConfigParser:
    """
    Read the configuration file and return a ConfigParser object.
    @param file_path: The path to the configuration file.
    @param verbose: Whether to print verbose output.
    @return: A ConfigParser object containing the configuration.
    """
    config = configparser.ConfigParser()
    try:
        expanded_path = os.path.expanduser(file_path)
        if os.path.exists(expanded_path):
            config.read(expanded_path)
            if verbose:
                print(f"✓ Konfiguration geladen: {expanded_path}")
        else:
            if verbose:
                print(f"⚠ Konfigurationsdatei nicht gefunden: {expanded_path}")
    except Exception as e:
        print(f"✗ Fehler beim Lesen der Konfiguration: {e}")
    
    return config

def get_overleaf_projects(config: configparser.ConfigParser, verbose: bool) -> dict[str, str]:
    """
    Extract Overleaf project mappings from config.
    @param config: ConfigParser object
    @param verbose: Whether to print verbose output
    @return: Dictionary mapping overleaf_id -> gitlab_paths
    """
    projects = {}
    if 'repos' in config:
        projects = dict(config['repos'])
        if verbose:
            print(f"✓ {len(projects)} Projekte in Konfiguration gefunden")
    return projects

def validate_config(config_path: str, verbose: bool) -> tuple[bool, str]:
    """
    Validate if configuration exists and is valid.
    @param config_path: Path to config file
    @param verbose: Whether to print verbose output
    @return: (is_valid, message)
    """
    expanded_path = os.path.expanduser(config_path)
    
    if not os.path.exists(expanded_path):
        return False, f"Konfigurationsdatei nicht gefunden: {expanded_path}"
    
    config = read_config(config_path, verbose)
    
    if 'repos' not in config:
        return False, "Keine [repos] Sektion in Konfigurationsdatei gefunden"
    
    projects = get_overleaf_projects(config, verbose)
    
    if not projects:
        return False, "Keine Projekt-Mappings in [repos] Sektion gefunden"
    
    # Validate format of mappings
    for overleaf_id, gitlab_paths in projects.items():
        if not overleaf_id.strip():
            return False, f"Leere Overleaf-ID gefunden"
        
        if not gitlab_paths.strip():
            return False, f"Leere GitLab-Pfade für Projekt {overleaf_id}"
    
    return True, f"Konfiguration ist gültig ({len(projects)} Projekte)"

def create_config_dir(config_path: str) -> None:
    """Create config directory if it doesn't exist."""
    expanded_path = os.path.expanduser(config_path)
    config_dir = os.path.dirname(expanded_path)
    
    # Fix: Only create directory if config_dir is not empty
    if config_dir:
        os.makedirs(config_dir, exist_ok=True)

def add_project_mapping(config_path: str, overleaf_id: str, gitlab_paths: str, verbose: bool) -> bool:
    """
    Add a new project mapping to config.
    @param config_path: Path to config file
    @param overleaf_id: Overleaf project ID
    @param gitlab_paths: Comma-separated GitLab repository paths
    @param verbose: Whether to print verbose output
    @return: Success status
    """
    try:
        expanded_path = os.path.expanduser(config_path)
        
        # Fix: Create directory for config file
        config_dir = os.path.dirname(expanded_path)
        if config_dir:  # Only if directory path is not empty
            os.makedirs(config_dir, exist_ok=True)
        
        config = configparser.ConfigParser()
        
        # Load existing config if it exists
        if os.path.exists(expanded_path):
            config.read(expanded_path)
        
        # Ensure [repos] section exists
        if 'repos' not in config:
            config.add_section('repos')
        
        # Add the mapping
        config.set('repos', overleaf_id, gitlab_paths)
        
        # Write back to file
        with open(expanded_path, 'w') as configfile:
            config.write(configfile)
        
        if verbose:
            print(f"✓ Projekt-Mapping hinzugefügt: {overleaf_id} -> {gitlab_paths}")
        
        return True
        
    except Exception as e:
        print(f"✗ Fehler beim Hinzufügen des Projekt-Mappings: {e}")
        return False

def interactive_config_setup(config_path: str, verbose: bool) -> bool:
    """
    Interactive setup for configuration.
    @param config_path: Path to config file
    @param verbose: Whether to print verbose output
    @return: Success status
    """
    print("\n=== Interaktive Konfiguration ===")
    print("Erstellen Sie ein neues Projekt-Mapping für Overleaf → GitLab Backup\n")
    
    try:
        # Get Overleaf project ID
        print("Schritt 1: Overleaf-Projekt-ID")
        print("Tipp: Finden Sie die ID in der URL Ihres Overleaf-Projekts")
        print("Beispiel: https://www.overleaf.com/project/662a5ab30650c57e5355029b")
        print("         Die ID wäre: 662a5ab30650c57e5355029b")
        
        overleaf_id = input("\nOverleaf-Projekt-ID eingeben: ").strip()
        if not overleaf_id:
            print("✗ Overleaf-ID darf nicht leer sein")
            return False
        
        # Get GitLab repository paths
        print(f"\nSchritt 2: GitLab-Repository-Pfade")
        print("Format: ssh-alias/namespace/repository.git")
        print("Beispiel: gitlab-urz/MackPhilip/mein-projekt.git")
        print("Mehrere Pfade durch Komma trennen für redundante Backups")
        
        gitlab_paths = input("\nGitLab-Repository-Pfad(e) eingeben: ").strip()
        if not gitlab_paths:
            print("✗ GitLab-Pfade dürfen nicht leer sein")
            return False
        
        # Confirm before saving
        print(f"\n=== Bestätigung ===")
        print(f"Overleaf-ID: {overleaf_id}")
        print(f"GitLab-Pfade: {gitlab_paths}")
        
        confirm = input("\nMapping speichern? (j/N): ").strip().lower()
        if confirm not in ['j', 'ja', 'y', 'yes']:
            print("Abgebrochen.")
            return False
        
        # Save the mapping
        success = add_project_mapping(config_path, overleaf_id, gitlab_paths, verbose)
        
        if success:
            print(f"\n✓ Konfiguration erfolgreich gespeichert: {os.path.expanduser(config_path)}")
            
            # Ask if user wants to add more projects
            more = input("\nWeiteres Projekt hinzufügen? (j/N): ").strip().lower()
            if more in ['j', 'ja', 'y', 'yes']:
                return interactive_config_setup(config_path, verbose)
        
        return success
        
    except KeyboardInterrupt:
        print("\n\nAbgebrochen.")
        return False
    except Exception as e:
        print(f"\n✗ Fehler bei der interaktiven Konfiguration: {e}")
        return False

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
    """Create config directory if it doesn't exist.
    @param config_path: Path to config file
    """
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

def list_existing_mappings(config: configparser.ConfigParser) -> None:
    """Display existing project mappings.
    @param config: ConfigParser object
    """
    projects = get_overleaf_projects(config, verbose=False)
    
    if not projects:
        print("Keine Projekt-Mappings gefunden.")
        return
    
    print("\n=== Bestehende Projekt-Mappings ===")
    for i, (overleaf_id, gitlab_paths) in enumerate(projects.items(), 1):
        print(f"{i}. Overleaf-ID: {overleaf_id}")
        print(f"   GitLab-Pfade: {gitlab_paths}")
        print()

def delete_project_mapping(config_path: str, overleaf_id: str, verbose: bool) -> bool:
    """Delete a project mapping from config.
    @param config_path: Path to config file
    @param overleaf_id: Overleaf project ID
    @param verbose: Whether to print verbose output
    @return: Success status
    """
    try:
        expanded_path = os.path.expanduser(config_path)
        
        if not os.path.exists(expanded_path):
            print("✗ Konfigurationsdatei nicht gefunden")
            return False
        
        config = configparser.ConfigParser()
        config.read(expanded_path)
        
        if 'repos' not in config or overleaf_id not in config['repos']:
            print(f"✗ Projekt {overleaf_id} nicht in Konfiguration gefunden")
            return False
        
        # Remove the mapping
        config.remove_option('repos', overleaf_id)
        
        # Write back to file
        with open(expanded_path, 'w') as configfile:
            config.write(configfile)
        
        if verbose:
            print(f"✓ Projekt-Mapping gelöscht: {overleaf_id}")
        
        return True
        
    except Exception as e:
        print(f"✗ Fehler beim Löschen des Projekt-Mappings: {e}")
        return False

def get_user_choice(prompt: str, valid_choices: list[str], allow_empty: bool = False) -> str:
    """Get user input with validation.
    @param prompt: Prompt message to display
    @param valid_choices: List of valid choices
    @param allow_empty: Whether to allow empty input
    @return: User's choice
    """
    while True:
        try:
            choice = input(prompt).strip().lower()
            
            if allow_empty and not choice:
                return ""

            if choice in [c.lower() for c in valid_choices]:
                return choice
            
            print(f"Ungültige Eingabe. Gültige Optionen: {', '.join(valid_choices)}")
            
        except KeyboardInterrupt:
            return "exit"

def add_single_mapping(config_path: str, verbose: bool) -> tuple[bool, str, str]:
    """Add a single project mapping. Returns (success, overleaf_id, gitlab_paths).
    @param config_path: Path to config file
    @param verbose: Whether to print verbose output
    @return: (success, overleaf_id, gitlab_paths)
    """
    print("\n=== Neues Projekt-Mapping hinzufügen ===")
    
    # Get Overleaf project ID
    print("Schritt 1: Overleaf-Projekt-ID")
    print("Tipp: Finden Sie die ID in der URL Ihres Overleaf-Projekts")
    print("Beispiel: https://www.overleaf.com/project/662a5ab30650c57e5355029b")
    print("         Die ID wäre: 662a5ab30650c57e5355029b")
    print("Eingabe: [Overleaf-ID] oder 'exit' zum Abbrechen")
    
    overleaf_id = input("\nOverleaf-Projekt-ID: ").strip()
    if not overleaf_id or overleaf_id.lower() == 'exit':
        return False, "", ""
    
    # Get GitLab repository paths (multiple possible)
    print(f"\nSchritt 2: GitLab-Repository-Pfade für '{overleaf_id}'")
    print("Format: ssh-alias/namespace/repository.git")
    print("Beispiel: gitlab-urz/MackPhilip/mein-projekt.git")
    print("Eingabe: [GitLab-Pfad], 'done' zum Beenden, 'exit' zum Abbrechen")
    
    gitlab_paths = []
    while True:
        path = input(f"\nGitLab-Pfad #{len(gitlab_paths)+1}: ").strip()
        
        if path.lower() == 'exit':
            return False, "", ""
        elif path.lower() == 'done':
            if gitlab_paths:
                break
            else:
                print("✗ Mindestens ein GitLab-Pfad erforderlich")
                continue
        elif path:
            gitlab_paths.append(path)
            print(f"✓ Pfad hinzugefügt: {path}")
        else:
            print("Leere Eingabe ignoriert. Verwenden Sie 'done' zum Beenden.")
    
    # Confirm before saving
    gitlab_paths_str = ", ".join(gitlab_paths)
    print(f"\n=== Bestätigung ===")
    print(f"Overleaf-ID: {overleaf_id}")
    print(f"GitLab-Pfade: {gitlab_paths_str}")
    
    choice = get_user_choice("\nMapping speichern? (j/n): ", ['j', 'ja', 'y', 'yes', 'n', 'no', 'nein'])
    if choice in ['j', 'ja', 'y', 'yes']:
        success = add_project_mapping(config_path, overleaf_id, gitlab_paths_str, verbose)
        if success:
            print(f"✓ Projekt-Mapping gespeichert: {overleaf_id}")
        return success, overleaf_id, gitlab_paths_str
    else:
        print("Abgebrochen.")
        return False, "", ""

def edit_existing_mappings(config_path: str, verbose: bool) -> bool:
    """Edit existing project mappings.
    @param config_path: Path to config file
    @param verbose: Whether to print verbose output
    @return: Success status
    """
    config = read_config(config_path, verbose)
    projects = get_overleaf_projects(config, verbose=False)
    
    if not projects:
        print("Keine Projekt-Mappings zum Bearbeiten gefunden.")
        return True
    
    while True:
        print("\n=== Bestehende Projekt-Mappings bearbeiten ===")
        project_list = list(projects.items())
        
        for i, (overleaf_id, gitlab_paths) in enumerate(project_list, 1):
            print(f"{i}. {overleaf_id} → {gitlab_paths}")
        
        print(f"{len(project_list)+1}. Zurück zum Hauptmenü")
        
        try:
            choice = input(f"\nProjekt auswählen (1-{len(project_list)+1}): ").strip()
            
            if not choice or choice == str(len(project_list)+1):
                return True
            
            index = int(choice) - 1
            if 0 <= index < len(project_list):
                overleaf_id, gitlab_paths = project_list[index]
                
                print(f"\nGewähltes Projekt: {overleaf_id}")
                print(f"Aktuelle GitLab-Pfade: {gitlab_paths}")
                
                action = get_user_choice(
                    "\nAktion wählen (edit/delete/back): ",
                    ['edit', 'delete', 'back']
                )
                
                if action == 'edit':
                    print(f"\nNeue GitLab-Pfade eingeben (aktuell: {gitlab_paths})")
                    print("Leer lassen um beizubehalten, 'exit' zum Abbrechen")
                    new_paths = input("Neue GitLab-Pfade: ").strip()
                    
                    if new_paths and new_paths.lower() != 'exit':
                        if add_project_mapping(config_path, overleaf_id, new_paths, verbose):
                            print(f"✓ Projekt {overleaf_id} aktualisiert")
                            projects[overleaf_id] = new_paths
                        else:
                            print(f"✗ Fehler beim Aktualisieren von {overleaf_id}")
                
                elif action == 'delete':
                    confirm = get_user_choice(
                        f"Projekt '{overleaf_id}' wirklich löschen? (j/n): ",
                        ['j', 'ja', 'y', 'yes', 'n', 'no', 'nein']
                    )
                    
                    if confirm in ['j', 'ja', 'y', 'yes']:
                        if delete_project_mapping(config_path, overleaf_id, verbose):
                            print(f"✓ Projekt {overleaf_id} gelöscht")
                            del projects[overleaf_id]
                        else:
                            print(f"✗ Fehler beim Löschen von {overleaf_id}")
                
                elif action == 'back':
                    continue
            else:
                print("Ungültige Auswahl.")
                
        except (ValueError, KeyboardInterrupt):
            print("\nZurück zum Hauptmenü.")
            return True

def interactive_config_setup(config_path: str, verbose: bool) -> bool:
    """
    Interactive setup for configuration with full menu system.
    @param config_path: Path to config file
    @param verbose: Whether to print verbose output
    @return: Success status
    """
    print("\n=== Interaktive Konfigurationsverwaltung ===")
    
    try:
        while True:
            # Load current config
            config = read_config(config_path, verbose)
            projects = get_overleaf_projects(config, verbose=False)
            
            # Show current state
            if projects:
                list_existing_mappings(config)
                action = get_user_choice(
                    "Aktion wählen (add/edit/done): ",
                    ['add', 'edit', 'done', 'exit']
                )
            else:
                print("Keine Konfiguration gefunden oder Datei ist leer.")
                action = get_user_choice(
                    "Möchten Sie Einträge hinzufügen oder beenden? (add/exit): ",
                    ['add', 'exit']
                )
            
            if action in ['exit', 'done']:
                print("Konfiguration beendet.")
                return True
            
            elif action == 'add':
                success, _, _ = add_single_mapping(config_path, verbose)
                if success:
                    # Ask if user wants to add more
                    more = get_user_choice(
                        "\nWeiteres Projekt hinzufügen? (add/done): ",
                        ['add', 'done', 'exit']
                    )
                    if more in ['done', 'exit']:
                        return True
            
            elif action == 'edit':
                edit_existing_mappings(config_path, verbose)
            
    except KeyboardInterrupt:
        print("\n\nKonfiguration abgebrochen.")
        return True
    except Exception as e:
        print(f"\n✗ Fehler bei der interaktiven Konfiguration: {e}")
        return False

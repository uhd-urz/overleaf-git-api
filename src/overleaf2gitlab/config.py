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
            return False, "Leere Overleaf-ID gefunden"
        
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
        print("\n✗ Keine Projekt-Mappings gefunden")
        return
    
    print("\n=== Bestehende Projekt-Mappings ===")
    for i, (overleaf_id, gitlab_paths) in enumerate(projects.items(), 1):
        print(f"{i}. Overleaf-ID: {overleaf_id}")
        print("   GitLab-Pfade:")
        for j, path in enumerate(gitlab_paths.split(','), 1):
            print(f"      {j}. {path.strip()}")
        print()

def edit_gitlab_paths(config: configparser.ConfigParser, config_path: str, overleaf_id: str, verbose: bool) -> bool:
    """Edit GitLab paths for a specific Overleaf project.
    @param config: ConfigParser object
    @param config_path: Path to config file
    @param overleaf_id: Overleaf project ID
    @param verbose: Whether to print verbose output
    @return: Success status
    """
    try:
        if 'repos' not in config or overleaf_id not in config['repos']:
            print(f"✗ Overleaf-Projekt {overleaf_id} nicht in Konfiguration gefunden")
            return False

        while True:
            # Get current paths
            gitlab_paths = [p.strip() for p in config['repos'][overleaf_id].split(',')]
            
            # Display main menu
            print("\n=== GitLab-Pfade bearbeiten ===")
            print(f"Overleaf-ID: {overleaf_id}")
            print("Aktuelle GitLab-Pfade:")
            for i, path in enumerate(gitlab_paths, 1):
                print(f"   {i}. {path}")
            
            print("\nOptionen:")
            print("   1. GitLab-Pfad hinzufügen")
            print("   2. GitLab-Pfad entfernen")
            print("   3. Alle GitLab-Pfade neu setzen")
            print("   4. Fertig")
            print("   5. Zurück")
            
            try:
                choice = int(input("\nAktion auswählen (1-5): "))
                if choice < 1 or choice > 5:
                    raise ValueError()
            except ValueError:
                print("✗ Ungültige Eingabe")
                continue
            
            if choice == 1:  # Add path
                new_path = input("\nNeuer GitLab-Pfad: ").strip()
                if new_path:
                    gitlab_paths.append(new_path)
                    config['repos'][overleaf_id] = ', '.join(gitlab_paths)
                    with open(config_path, 'w') as f:
                        config.write(f)
                    print(f"\n✓ Pfad '{new_path}' wurde hinzugefügt")
            
            elif choice == 2:  # Remove path
                if not gitlab_paths:
                    print("\n✗ Keine GitLab-Pfade vorhanden")
                    continue
                    
                print("\n--- GitLab-Pfad entfernen ---")
                print("Aktuelle Pfade:")
                for i, path in enumerate(gitlab_paths, 1):
                    print(f"   {i}. {path}")
                print(f"   {len(gitlab_paths) + 1}. Abbrechen")
                
                try:
                    del_choice = int(input(f"\nPfad auswählen (1-{len(gitlab_paths) + 1}): "))
                    if del_choice < 1 or del_choice > len(gitlab_paths) + 1:
                        raise ValueError()
                    if del_choice == len(gitlab_paths) + 1:  # Cancel
                        continue
                    
                    removed_path = gitlab_paths.pop(del_choice - 1)
                    
                    # Check if this was the last path
                    if not gitlab_paths:
                        confirm = input("\nHinweis: Keine GitLab-Pfade mehr vorhanden.\n" +
                                     f"Möchten Sie die Overleaf-ID {overleaf_id} komplett löschen? (j/n): ")
                        if confirm.lower() == 'j':
                            del config['repos'][overleaf_id]
                            print(f"\n✓ Overleaf-Projekt {overleaf_id} wurde komplett gelöscht")
                            with open(config_path, 'w') as f:
                                config.write(f)
                            return True
                        else:
                            # Restore the removed path if user doesn't want to delete everything
                            gitlab_paths.append(removed_path)
                            print("\n✗ Löschvorgang abgebrochen")
                            continue
                    
                    # Update config with remaining paths
                    config['repos'][overleaf_id] = ', '.join(gitlab_paths)
                    with open(config_path, 'w') as f:
                        config.write(f)
                    print(f"\n✓ Pfad '{removed_path}' wurde entfernt")
                    print("\nAktuelle GitLab-Pfade:")
                    for i, path in enumerate(gitlab_paths, 1):
                        print(f"   {i}. {path}")
                        
                except ValueError:
                    print("✗ Ungültige Eingabe")
                    continue
            
            elif choice == 3:  # Reset all paths
                new_paths = input("\nNeue GitLab-Pfade (kommagetrennt): ").strip()
                if new_paths:
                    config['repos'][overleaf_id] = new_paths
                    with open(config_path, 'w') as f:
                        config.write(f)
                    print("\n✓ GitLab-Pfade wurden aktualisiert")
            
            elif choice in (4, 5):  # Done or Back
                return True
                
    except Exception as e:
        print(f"✗ Fehler beim Bearbeiten der GitLab-Pfade: {str(e)}")
        return False

def edit_existing_mappings(config_path: str, verbose: bool) -> bool:
    """Edit existing project mappings.
    @param config_path: Path to config file
    @param verbose: Whether to print verbose output
    @return: Success status
    """
    try:
        config = read_config(config_path, verbose)
        projects = get_overleaf_projects(config, verbose)
        
        if not projects:
            print("✗ Keine Projekt-Mappings gefunden")
            return False
        
        while True:
            list_existing_mappings(config)
            
            # Get Overleaf ID selection
            print("\nWählen Sie ein Projekt zum Bearbeiten (oder 'q' zum Beenden): ")
            choice = input("Overleaf-ID: ").strip().lower()
            
            if choice == 'q':
                return True
            
            if choice not in projects:
                print(f"✗ Ungültige Overleaf-ID: {choice}")
                continue
            
            # Edit paths for selected project
            if not edit_gitlab_paths(config, config_path, choice, verbose):
                print("✗ Bearbeitung fehlgeschlagen")
                continue
                
            # Reload config in case of changes
            config = read_config(config_path, verbose)
                
    except Exception as e:
        print(f"✗ Fehler beim Bearbeiten der Mappings: {str(e)}")
        return False
        
    return True

def get_user_choice(prompt: str, valid_choices: list[str], allow_empty: bool = False) -> str:
    """Get user input with validation.
    @param prompt: Prompt message to display
    @param valid_choices: List of valid choices
    @param allow_empty: Whether to allow empty input
    @return: User's choice
    """
    while True:
        choice = input(prompt).strip().lower()
        
        if not choice:
            if allow_empty:
                return choice
            print("✗ Keine Eingabe")
            continue
            
        if choice not in valid_choices:
            print("✗ Ungültige Eingabe")
            continue
            
        return choice

def add_single_mapping(config_path: str, verbose: bool) -> tuple[bool, str, str]:
    """Add a single project mapping. Returns (success, overleaf_id, gitlab_paths).
    @param config_path: Path to config file
    @param verbose: Whether to print verbose output
    @return: (success, overleaf_id, gitlab_paths)
    """
    print("\n=== Neues Projekt-Mapping hinzufügen ===")
    
    # Get Overleaf project ID
    print("\nSchritt 1: Overleaf-Projekt-ID")
    print("Tipp: Finden Sie die ID in der URL Ihres Overleaf-Projekts")
    print("Beispiel: https://www.overleaf.com/project/662a5ab30650c57e5355029b")
    print("         Die ID wäre: 662a5ab30650c57e5355029b")
    print("\nEingabe: [Overleaf-ID] oder 'exit' zum Abbrechen")
    
    overleaf_id = input("\nOverleaf-Projekt-ID: ").strip()
    if not overleaf_id or overleaf_id.lower() == 'exit':
        return False, "", ""
    
    # Get GitLab repository paths (multiple possible)
    print(f"\nSchritt 2: GitLab-Repository-Pfade für '{overleaf_id}'")
    print("Format: ssh-alias/namespace/repository.git")
    print("Beispiel: gitlab-urz/MackPhilip/mein-projekt.git")
    print("\nEingabe: [GitLab-Pfad], 'done' zum Beenden, 'exit' zum Abbrechen")
    
    gitlab_paths = []
    while True:
        path = input("\nGitLab-Pfad: ").strip()
        
        if not path or path.lower() == 'exit':
            return False, "", ""
            
        if path.lower() == 'done':
            if not gitlab_paths:
                print("✗ Sie müssen mindestens einen GitLab-Pfad angeben")
                continue
            break
            
        gitlab_paths.append(path)
        print(f"✓ Pfad hinzugefügt: {path}")
        print("Geben Sie 'done' ein, wenn Sie fertig sind")
    
    # Confirm before saving
    gitlab_paths_str = ", ".join(gitlab_paths)
    print(f"\n=== Bestätigung ===")
    print(f"Overleaf-ID: {overleaf_id}")
    print(f"GitLab-Pfade: {gitlab_paths_str}")
    
    choice = get_user_choice("\nMapping speichern? (j/n): ", ['j', 'ja', 'y', 'yes', 'n', 'no', 'nein'])
    if choice in ['j', 'ja', 'y', 'yes']:
        return True, overleaf_id, gitlab_paths_str
    else:
        return False, "", ""

def interactive_config_setup(config_path: str, verbose: bool) -> bool:
    """Interactive setup for configuration with full menu system.
    @param config_path: Path to config file
    @param verbose: Whether to print verbose output
    @return: Success status
    """
    print("\n=== Interaktive Konfigurationsverwaltung ===")
    
    try:
        while True:
            print("\nOptionen:")
            print("1. Neues Projekt-Mapping hinzufügen")
            print("2. Bestehende Mappings bearbeiten")
            print("3. Beenden")
            
            try:
                choice = int(input("\nAktion auswählen (1-3): "))
                if choice < 1 or choice > 3:
                    raise ValueError()
            except ValueError:
                print("✗ Ungültige Eingabe")
                continue
            
            if choice == 1:  # Add new mapping
                success, overleaf_id, gitlab_paths = add_single_mapping(config_path, verbose)
                if success:
                    if add_project_mapping(config_path, overleaf_id, gitlab_paths, verbose):
                        print("\n✓ Projekt-Mapping erfolgreich gespeichert")
                    else:
                        print("\n✗ Fehler beim Speichern des Projekt-Mappings")
            
            elif choice == 2:  # Edit existing mappings
                edit_existing_mappings(config_path, verbose)
            
            elif choice == 3:  # Exit
                print("\nKonfigurationsverwaltung beendet")
                return True
            
    except KeyboardInterrupt:
        print("\n\nKonfigurationsverwaltung abgebrochen")
        return False
        
    except Exception as e:
        print(f"\n✗ Unerwarteter Fehler: {str(e)}")
        return False
    
    return True

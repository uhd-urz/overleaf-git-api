import configparser
import os
from typing import Tuple
from .operations import read_config, get_overleaf_projects, write_config

def get_user_choice(prompt: str, valid_choices: list[str], allow_empty: bool = False) -> str:
    """Get validated user input."""
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

def list_existing_mappings(config: configparser.ConfigParser) -> None:
    """Display all project mappings."""
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

def add_single_mapping(config_path: str, verbose: bool) -> Tuple[bool, str, str]:
    """Add new project mapping interactively."""
    print("\n=== Neues Projekt-Mapping hinzufügen ===")
    
    # Get Overleaf ID
    print("\nSchritt 1: Overleaf-Projekt-ID")
    print("Tipp: Finden Sie die ID in der URL Ihres Overleaf-Projekts")
    print("Beispiel: https://www.overleaf.com/project/662a5ab30650c57e5355029b")
    print("         Die ID wäre: 662a5ab30650c57e5355029b")
    
    overleaf_id = input("\nOverleaf-Projekt-ID: ").strip()
    if not overleaf_id or overleaf_id.lower() == 'exit':
        return False, "", ""
    
    # Get GitLab paths
    print(f"\nSchritt 2: GitLab-Repository-Pfade für '{overleaf_id}'")
    print("Format: ssh-alias/namespace/repository.git")
    print("Beispiel: gitlab-urz/MackPhilip/mein-projekt.git")
    
    gitlab_paths = []
    while True:
        path = input("\nGitLab-Pfad (oder 'done'/'exit'): ").strip()
        
        if not path or path.lower() == 'exit':
            return False, "", ""
            
        if path.lower() == 'done':
            if not gitlab_paths:
                print("✗ Sie müssen mindestens einen GitLab-Pfad angeben")
                continue
            break
            
        gitlab_paths.append(path)
        print(f"✓ Pfad hinzugefügt: {path}")
    
    # Confirm
    gitlab_paths_str = ", ".join(gitlab_paths)
    print(f"\n=== Bestätigung ===")
    print(f"Overleaf-ID: {overleaf_id}")
    print(f"GitLab-Pfade: {gitlab_paths_str}")
    
    choice = get_user_choice("\nMapping speichern? (j/n): ", 
                           ['j', 'ja', 'y', 'yes', 'n', 'no', 'nein'])
    
    if choice in ['j', 'ja', 'y', 'yes']:
        return True, overleaf_id, gitlab_paths_str
    
    return False, "", ""

def edit_gitlab_paths(config: configparser.ConfigParser, config_path: str, 
                     overleaf_id: str, verbose: bool) -> bool:
    """Edit GitLab paths for a project."""
    try:
        if 'repos' not in config or overleaf_id not in config['repos']:
            print(f"✗ Overleaf-Projekt {overleaf_id} nicht in Konfiguration gefunden")
            return False

        while True:
            # Get current paths
            gitlab_paths = config['repos'][overleaf_id].split(',')
            gitlab_paths = [p.strip() for p in gitlab_paths]
            
            print("\n=== GitLab-Pfade bearbeiten ===")
            print(f"Overleaf-ID: {overleaf_id}")
            print("Aktuelle GitLab-Pfade:")
            for i, path in enumerate(gitlab_paths, 1):
                print(f"   {i}. {path}")
            
            print("\nOptionen:")
            print("1. GitLab-Pfad hinzufügen")
            print("2. GitLab-Pfad entfernen")
            print("3. Alle GitLab-Pfade neu setzen")
            print("4. Fertig")
            print("5. Zurück")
            
            try:
                choice = int(input("\nAktion auswählen (1-5): "))
                if choice < 1 or choice > 5:
                    raise ValueError()
            except ValueError:
                print("✗ Ungültige Eingabe")
                continue
            
            if choice == 1:  # Add
                new_path = input("\nNeuer GitLab-Pfad: ").strip()
                if new_path:
                    gitlab_paths.append(new_path)
                    config['repos'][overleaf_id] = ', '.join(gitlab_paths)
                    write_config(config, config_path)
                    print(f"\n✓ Pfad '{new_path}' wurde hinzugefügt")
            
            elif choice == 2:  # Remove
                if not gitlab_paths:
                    print("\n✗ Keine GitLab-Pfade vorhanden")
                    continue
                    
                print("\n--- GitLab-Pfad entfernen ---")
                for i, path in enumerate(gitlab_paths, 1):
                    print(f"   {i}. {path}")
                print(f"   {len(gitlab_paths) + 1}. Abbrechen")
                
                try:
                    idx = int(input(f"\nPfad auswählen (1-{len(gitlab_paths) + 1}): "))
                    if idx < 1 or idx > len(gitlab_paths) + 1:
                        raise ValueError()
                    
                    if idx == len(gitlab_paths) + 1:  # Cancel
                        continue
                    
                    removed = gitlab_paths.pop(idx - 1)
                    
                    if not gitlab_paths:
                        confirm = input("\nHinweis: Keine GitLab-Pfade mehr vorhanden.\n" +
                                     f"Möchten Sie die Overleaf-ID {overleaf_id} komplett löschen? (j/n): ")
                        if confirm.lower() == 'j':
                            del config['repos'][overleaf_id]
                            write_config(config, config_path)
                            print(f"\n✓ Overleaf-Projekt {overleaf_id} wurde gelöscht")
                            return True
                        gitlab_paths.append(removed)
                        print("\n✗ Löschvorgang abgebrochen")
                        continue
                    
                    config['repos'][overleaf_id] = ', '.join(gitlab_paths)
                    write_config(config, config_path)
                    print(f"\n✓ Pfad '{removed}' wurde entfernt")
                    
                except ValueError:
                    print("✗ Ungültige Eingabe")
                    continue
            
            elif choice == 3:  # Reset all
                new_paths = input("\nNeue GitLab-Pfade (kommagetrennt): ").strip()
                if new_paths:
                    config['repos'][overleaf_id] = new_paths
                    write_config(config, config_path)
                    print("\n✓ GitLab-Pfade wurden aktualisiert")
            
            elif choice in (4, 5):  # Done or Back
                return True
                
    except Exception as e:
        print(f"✗ Fehler beim Bearbeiten der GitLab-Pfade: {str(e)}")
        return False

def interactive_config_setup(config_path: str, verbose: bool) -> bool:
    """Interactive configuration management."""
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
            
            config = read_config(config_path, verbose)
            
            if choice == 1:  # Add new
                success, overleaf_id, gitlab_paths = add_single_mapping(config_path, verbose)
                if success:
                    if not 'repos' in config:
                        config.add_section('repos')
                    config['repos'][overleaf_id] = gitlab_paths
                    if write_config(config, config_path):
                        print("\n✓ Projekt-Mapping erfolgreich gespeichert")
            
            elif choice == 2:  # Edit existing
                projects = get_overleaf_projects(config, verbose)
                if not projects:
                    print("✗ Keine Projekt-Mappings gefunden")
                    continue
                
                while True:
                    list_existing_mappings(config)
                    
                    overleaf_id = input("\nWählen Sie ein Projekt zum Bearbeiten (oder 'q' zum Beenden): ").strip()
                    if overleaf_id.lower() == 'q':
                        break
                    
                    if overleaf_id not in projects:
                        print(f"✗ Ungültige Overleaf-ID: {overleaf_id}")
                        continue
                    
                    if not edit_gitlab_paths(config, config_path, overleaf_id, verbose):
                        print("✗ Bearbeitung fehlgeschlagen")
            
            elif choice == 3:  # Exit
                print("\nKonfigurationsverwaltung beendet")
                return True
            
    except KeyboardInterrupt:
        print("\n\nKonfigurationsverwaltung abgebrochen")
        return False
    except Exception as e:
        print(f"\n✗ Unerwarteter Fehler: {str(e)}")
        return False

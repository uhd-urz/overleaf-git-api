from .parser import get_args, check_global_arguments
from .config import read_config, get_overleaf_projects, validate_config, interactive_config_setup
from .backup import backup_overleaf_project
from configparser import ConfigParser


def handle_init_command(config_path: str, verbose: bool) -> bool:
    """
    Handle the init command for configuration validation and setup.
    @param config_path: Path to config file
    @param verbose: Whether to print verbose output
    @return: Success status
    """
    print("=== Overleaf2GitLab Konfiguration ===\n")
    
    # Validate existing config
    is_valid, message = validate_config(config_path, verbose)
    
    if is_valid:
        print(f"✓ {message}")
        
        # Ask if user wants to add more projects
        try:
            add_more = input("\nWeiteres Projekt-Mapping hinzufügen? (j/N): ").strip().lower()
            if add_more in ['j', 'ja', 'y', 'yes']:
                return interactive_config_setup(config_path, verbose)
            else:
                print("Konfiguration ist bereits gültig. Keine Änderungen vorgenommen.")
                return True
        except KeyboardInterrupt:
            print("\nAbgebrochen.")
            return True
    
    else:
        print(f"⚠ {message}")
        print("\nMögliche Aktionen:")
        print("1. Neue Konfiguration erstellen")
        print("2. Bestehendes Projekt-Mapping hinzufügen")
        print("3. Abbrechen")
        
        try:
            choice = input("\nWählen Sie eine Option (1-3): ").strip()
            
            if choice == '1' or choice == '2':
                return interactive_config_setup(config_path, verbose)
            elif choice == '3':
                print("Abgebrochen.")
                return False
            else:
                print("Ungültige Auswahl.")
                return False
                
        except KeyboardInterrupt:
            print("\nAbgebrochen.")
            return False

def backup_single_project(overleaf_id: str, available_projects: dict[str, str], cache_dir: str, clean: bool, verbose: bool):
    # check if overleaf id is a key in available_projects
    if overleaf_id not in available_projects:
        print(f"✗ Overleaf-Projekt {overleaf_id} nicht in Konfiguration gefunden")
        print("Verfügbare Projekte:")
        for proj_id in available_projects.keys():
            print(f"  - {proj_id}")
        return False
    
    gitlab_paths = available_projects[overleaf_id].split(',')
    gitlab_paths = [path.strip() for path in gitlab_paths]
    
    return backup_overleaf_project(overleaf_id, gitlab_paths, cache_dir, clean, verbose)

def backup_all_projects(available_projects: dict[str, str], cache_dir: str, clean: bool, verbose: bool):
    success_count = 0
    total_count = len(available_projects)
    
    for overleaf_id, gitlab_paths_str in available_projects.items():
        gitlab_paths = [path.strip() for path in gitlab_paths_str.split(',')]
        
        if backup_overleaf_project(overleaf_id, gitlab_paths, cache_dir, clean, verbose):
            success_count += 1
        else:
            print(f"✗ Backup für Projekt {overleaf_id} fehlgeschlagen")
    
    print(f"\nBackup abgeschlossen: {success_count}/{total_count} Projekte erfolgreich")
    return success_count == total_count

def main():
    args = get_args()
    
    # Handle config command separately
    if args.command == "config":
        success = handle_init_command(args.config, args.verbose)
        exit(0 if success else 1)
    
    # For backup commands, validate config first
    is_valid, message = validate_config(args.config, args.verbose)
    
    if not is_valid:
        print(f"✗ {message}")
        print(f"Führen Sie 'overleaf2gitlab config' aus, um die Konfiguration zu erstellen.")
        exit(1)
    
    # Load configuration
    success, config_path, cache_dir, clean, verbose = check_global_arguments(args)
    if not success:
        print("✗ Ungültige Argumente")
        exit(1)
    
    config = read_config(config_path, verbose)
    available_projects = get_overleaf_projects(config, verbose)
    
    if not available_projects:
        print("✗ Keine Projekte in Konfiguration gefunden")
        print("Führen Sie 'overleaf2gitlab config' aus, um Projekte zu konfigurieren.")
        exit(1)
    
    # Handle backup commands
    if args.command == "backup-single":
        success = backup_single_project(args.overleaf_id, available_projects, cache_dir, clean, verbose)
        exit(0 if success else 1)
    
    elif args.command == "backup-all":
        success = backup_all_projects(available_projects, cache_dir, clean, verbose)
        exit(0 if success else 1)
    
    else:
        print("✗ Unbekannter Befehl. Verwenden Sie --help für verfügbare Befehle.")
        exit(1)

if __name__ == "__main__":
    main()

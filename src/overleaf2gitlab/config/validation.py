from .operations import read_config, get_overleaf_projects

def validate_config(config_path: str, verbose: bool) -> tuple[bool, str]:
    """Validate configuration file and contents."""
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

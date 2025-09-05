import configparser
import os
from typing import Dict

def read_config(file_path: str, verbose: bool) -> configparser.ConfigParser:
    """Read and parse configuration file."""
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

def get_overleaf_projects(config: configparser.ConfigParser, verbose: bool) -> Dict[str, str]:
    """Extract Overleaf project mappings from config."""
    projects = {}
    if 'repos' in config:
        projects = dict(config['repos'])
        if verbose:
            print(f"✓ {len(projects)} Projekte in Konfiguration gefunden")
    return projects

def write_config(config: configparser.ConfigParser, config_path: str) -> bool:
    """Write configuration to file safely."""
    try:
        expanded_path = os.path.expanduser(config_path)
        config_dir = os.path.dirname(expanded_path)
        
        if config_dir:
            os.makedirs(config_dir, exist_ok=True)
            
        with open(expanded_path, 'w') as f:
            config.write(f)
        return True
    except Exception as e:
        print(f"✗ Fehler beim Schreiben der Konfiguration: {e}")
        return False

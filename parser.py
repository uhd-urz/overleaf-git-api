from argparse import ArgumentParser, Namespace
from os.path import exists, expanduser
from os import makedirs

def get_args() -> Namespace:
    "Argument parser for Overleaf to GitLab backup tool"
    parser = ArgumentParser(description="Overleaf git api to gitlab for backup restoration")
    
    # Global arguments
    parser.add_argument("--verbose",
                        action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--config",
                        type=str,
                        default="~/.config/overleaf2gitlab/config.ini",
                        help="Path to configuration file with Overleaf ID and GitLab URL mappings")
    parser.add_argument("--cache-dir",
                        type=str,
                        default="~/.local/share/overleaf2gitlab",
                        help="Cache directory for git operations")
    parser.add_argument("--clean-cache",
                        action="store_true",
                        help="Clean cache directory before backup")

    subparsers = parser.add_subparsers(dest="command", required=True, help="Available commands")

    # Backup single command
    backup_single_parser = subparsers.add_parser("backup-single", help="Backup single Overleaf project to GitLab")
    backup_single_parser.add_argument("overleaf_id",
                                       help="Overleaf project ID to backup")

    # Backup all command
    # backup_all_parser = subparsers.add_parser("backup-all", help="Backup all Overleaf projects from config to GitLab")

    return parser.parse_args()


def check_global_arguments(args: Namespace) -> tuple[bool, str, str, bool, str]:
    # Check and print global arguments
    if args.verbose:
        print("Verbose mode is enabled")
        print(f"Using cache directory: {args.cache_dir}")
        print(f"Using configuration file: {args.config}")
        print(f"Clean cache backup: {args.clean_cache}")
        print(f"Command: {args.command}")

    # Expandiere ~ zu Home-Verzeichnis
    config_path = expanduser(args.config)
    cache_dir_path = expanduser(args.cache_dir)

    # check if config file exists
    if not exists(config_path):
        raise FileNotFoundError(f"Configuration file '{config_path}' does not exist. please use `--config` to specify a valid config file.")
    
    # Create cache directory if it does not exist
    if not exists(cache_dir_path):
        makedirs(cache_dir_path)
        if args.verbose:
            print(f"Created cache directory: {cache_dir_path}")
    
    return args.verbose, cache_dir_path, config_path, args.clean_cache, args.command
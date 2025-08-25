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
                        default="~/.config/overleaf2gitlab/config.ini",
                        help="Path to configuration file")
    
    parser.add_argument("--cache-dir",
                        default="~/.cache/overleaf2gitlab",
                        help="Directory for temporary git repositories")
    
    parser.add_argument("--clean",
                        action="store_true",
                        help="Clean cache after backup")

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Config command
    config_parser = subparsers.add_parser("config", help="Configure project mappings")
    
    # Backup single command
    single_parser = subparsers.add_parser("backup-single", help="Backup single Overleaf project")
    single_parser.add_argument("overleaf_id", help="Overleaf project ID")
    
    # Backup all command
    all_parser = subparsers.add_parser("backup-all", help="Backup all configured projects")
    
    return parser.parse_args()


def check_global_arguments(args: Namespace) -> tuple[bool, str, str, bool, bool]:
    # Check and print global arguments
    if args.verbose:
        print("Verbose mode is enabled")
        print(f"Using cache directory: {args.cache_dir}")
        print(f"Using configuration file: {args.config}")
        print(f"Clean cache backup: {args.clean}")
        print(f"Command: {args.command}")

    # Expandiere ~ zu Home-Verzeichnis
    config_path = expanduser(args.config)
    cache_dir_path = expanduser(args.cache_dir)

    # check if config file exists (remove this check for config command)
    # if not exists(config_path):
    #     raise FileNotFoundError(f"Configuration file '{config_path}' does not exist. please use `--config` to specify a valid config file.")
    
    # Create cache directory if it does not exist
    if not exists(cache_dir_path):
        makedirs(cache_dir_path)
        if args.verbose:
            print(f"Created cache directory: {cache_dir_path}")
    
    return True, config_path, cache_dir_path, args.clean, args.verbose
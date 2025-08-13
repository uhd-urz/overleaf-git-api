from parser import get_args, check_global_arguments
from config import read_config, get_overleaf_projects
from backup import backup_overleaf_project
from configparser import ConfigParser


def backup_single_project(overleaf_id: str, available_projects: dict[str, str], cache_dir: str, clean: bool, verbose: bool):
    # check if overleaf id is a key in available_projects
    if overleaf_id not in available_projects:
        print(f"Overleaf project ID '{overleaf_id}' not found in available projects.")
        print(f"Available projects:")
        for proj_id in available_projects.keys():
            print(f" - {proj_id}")
        return
    
    gitlab_urls = available_projects[overleaf_id]
    gitlab_paths = gitlab_urls.split(", ")
    
    # Use the complete backup workflow
    success = backup_overleaf_project(overleaf_id=overleaf_id, gitlab_paths=gitlab_paths, cache_dir=cache_dir, clean=clean, verbose=verbose)

    if success:
        print("Backup completed successfully!")
    else:
        print("Backup failed!")


def backup_all_projects(available_projects: dict[str, str], cache_dir: str, clean: bool, verbose: bool):
    for overleaf_id, gitlab_urls in available_projects.items():
        if verbose:
            print(f"Backing up Overleaf project '{overleaf_id}' to GitLab SSH alias: {gitlab_urls}")
        gitlab_urls_list = gitlab_urls.split(", ")
        success = backup_overleaf_project(overleaf_id=overleaf_id, gitlab_paths=gitlab_urls_list, cache_dir=cache_dir, clean=clean, verbose=verbose)
        if success:
            print(f"Backup completed successfully for project '{overleaf_id}'!")
        else:
            print(f"Backup failed for project '{overleaf_id}'!")
    print("All projects processed.")

def main():
    args = get_args()
    verbose, cache_dir, config, clean_cache, command = check_global_arguments(args)
    config_data: ConfigParser = read_config(file_path=config, verbose=verbose)

    available_overleaf_projects: dict[str, str] = get_overleaf_projects(config=config_data, verbose=verbose)

    if command == "backup-single":
        # Get Overleaf project ID
        overleaf_id = args.overleaf_id
        print(f"Backing up single Overleaf project: {overleaf_id}")
        backup_single_project(overleaf_id=overleaf_id, available_projects=available_overleaf_projects, cache_dir=cache_dir, clean=clean_cache, verbose=verbose)
    elif command == "backup-all":
        print("Backing up all Overleaf projects")
        backup_all_projects(available_projects=available_overleaf_projects, cache_dir=cache_dir, clean=clean_cache, verbose=verbose)
    else:
        print("Invalid command")
        pass

if __name__ == "__main__":
    main()

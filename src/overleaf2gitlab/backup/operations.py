import os
import subprocess
from pathlib import Path
from .git import get_all_git_remotes, get_git_remote_url

def mk_cache_overleaf_dir(overleaf_id: str, cache_dir: str) -> None:
    """Create the cache directory for the Overleaf project."""
    os.makedirs(os.path.join(cache_dir, f"overleaf_{overleaf_id}"), exist_ok=True)

def check_cache_overleaf_git_existence(overleaf_id: str, cache_dir: str) -> bool:
    """Check if the Overleaf project directory exists and is a git repository."""
    return os.path.exists(os.path.join(cache_dir, f"overleaf_{overleaf_id}", ".git"))

def mk_cache_overleaf_git_dir(overleaf_id: str, cache_dir: str) -> None:
    """Create and initialize git repository for the Overleaf project."""
    if not check_cache_overleaf_git_existence(overleaf_id, cache_dir):
        mk_cache_overleaf_dir(overleaf_id, cache_dir)
        repo_path = os.path.join(cache_dir, f"overleaf_{overleaf_id}")
        
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        
        credentials_dir = Path.home() / ".gitconfig.d"
        credentials_dir.mkdir(exist_ok=True)
        credentials_file = credentials_dir / "overleaf"
        
        subprocess.run([
            "git", "config", "--local", "credential.helper", 
            f"store --file={credentials_file}"
        ], cwd=repo_path, check=True)

def setup_git_remotes(overleaf_id: str, gitlab_paths: list[str], cache_dir: str) -> bool:
    """Setup/update git remotes to match expected configuration."""
    repo_path = os.path.join(cache_dir, f"overleaf_{overleaf_id}")
    
    if not check_cache_overleaf_git_existence(overleaf_id, cache_dir):
        print(f"Creating git repository in {repo_path}")
        mk_cache_overleaf_git_dir(overleaf_id, cache_dir)
    
    try:
        origin_url = f"https://git.overleaf.com/{overleaf_id}"
        current_remotes = get_all_git_remotes(repo_path)
        
        # Set/update origin remote
        if "origin" in current_remotes:
            if current_remotes["origin"] != origin_url:
                subprocess.run(["git", "remote", "set-url", "origin", origin_url], 
                             cwd=repo_path, check=True)
        else:
            subprocess.run(["git", "remote", "add", "origin", origin_url], 
                         cwd=repo_path, check=True)
        
        # Setup backup remotes
        for i, gitlab_path in enumerate(gitlab_paths):
            backup_name = f"backup{i}"
            backup_url = f"ssh://{gitlab_path}"
            
            if backup_name in current_remotes:
                if current_remotes[backup_name] != backup_url:
                    subprocess.run(["git", "remote", "set-url", backup_name, backup_url], 
                                 cwd=repo_path, check=True)
            else:
                subprocess.run(["git", "remote", "add", backup_name, backup_url], 
                             cwd=repo_path, check=True)
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error setting up git remotes: {e}")
        return False

def sync_repositories(overleaf_id: str, cache_dir: str, verbose: bool = False) -> bool:
    """Sync repositories: pull from overleaf -> push to backups."""
    repo_path = os.path.join(cache_dir, f"overleaf_{overleaf_id}")
    
    if not check_cache_overleaf_git_existence(overleaf_id, cache_dir):
        print(f"Error: Git repository not found in {repo_path}")
        return False
    
    try:
        # 1. Pull from Overleaf (master branch)
        if verbose:
            print(f"Pulling from Overleaf for project {overleaf_id}...")
        
        subprocess.run([
            "git", "pull", "origin", "master"
        ], cwd=repo_path, check=True, capture_output=not verbose)
        print(f"✓ Successfully pulled from origin/master")
        
        # 2. Push to backup remotes (master branch)
        current_remotes = get_all_git_remotes(repo_path)
        backup_remotes = [name for name in current_remotes.keys() if name.startswith('backup')]
        
        if not backup_remotes:
            print("Warning: No backup remotes found")
            return True
        
        for remote in sorted(backup_remotes):
            if verbose:
                print(f"Pushing to {remote} ({current_remotes[remote]})...")
            
            try:
                subprocess.run([
                    "git", "push", remote, "master"
                ], cwd=repo_path, check=True, capture_output=not verbose)
                print(f"✓ Successfully pushed to {remote}")
                
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to push to {remote}: {e}")
                continue
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during sync: {e}")
        return False

def backup_overleaf_project(overleaf_id: str, gitlab_paths: list[str], cache_dir: str, clean: bool, verbose: bool = False) -> bool:
    """Complete backup workflow for a single Overleaf project."""
    print(f"\n{'='*60}")
    print(f"Starting backup for Overleaf project: {overleaf_id}")
    print(f"GitLab paths: {gitlab_paths}")
    print(f"{'='*60}")
    
    if not setup_git_remotes(overleaf_id, gitlab_paths, cache_dir):
        print(f"✗ Failed to setup git remotes for {overleaf_id}")
        return False
    
    if not sync_repositories(overleaf_id, cache_dir, verbose):
        print(f"✗ Failed to sync repositories for {overleaf_id}")
        return False
    
    print(f"✓ Backup completed successfully for {overleaf_id}")
    
    if clean:
        cache_path = os.path.join(cache_dir, f"overleaf_{overleaf_id}")
        try:
            subprocess.run(["rm", "-rf", cache_path], check=True)
            print(f"✓ Cleaned up cache directory: {cache_path}")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Failed to clean cache: {e}")
    
    return True

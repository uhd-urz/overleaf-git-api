import os
import subprocess
from pathlib import Path

def mk_cache_overleaf_dir(overleaf_id, cache_dir) -> None:
    """Create the cache directory for the Overleaf project.
    @param overleaf_id: The Overleaf project ID
    @param cache_dir: The cache directory path
    """
    os.makedirs(os.path.join(cache_dir, f"overleaf_{overleaf_id}"), exist_ok=True)

def check_cache_overleaf_git_existence(overleaf_id, cache_dir) -> bool:
    """Check if the Overleaf project directory exists and is a git repository.
    @param overleaf_id: The Overleaf project ID
    @param cache_dir: The cache directory path
    @return: True if the directory exists and is a git repository, False otherwise
    """
    return os.path.exists(os.path.join(cache_dir, f"overleaf_{overleaf_id}", ".git"))

def mk_cache_overleaf_git_dir(overleaf_id, cache_dir) -> None:
    """Create the cache directory for the Overleaf project.
    @param overleaf_id: The Overleaf project ID
    @param cache_dir: The cache directory path
    """
    if not check_cache_overleaf_git_existence(overleaf_id, cache_dir):
        # Create directory first
        mk_cache_overleaf_dir(overleaf_id, cache_dir)
        repo_path = os.path.join(cache_dir, f"overleaf_{overleaf_id}")
        
        # Run git init
        subprocess.run(["git", "init"], cwd=repo_path, check=True)
        
        # git config --local credential.helper store --file=/home/phil/.gitconfig.d/overleaf
        credentials_dir = Path.home() / ".gitconfig.d"
        credentials_dir.mkdir(exist_ok=True)
        credentials_file = credentials_dir / "overleaf"
        
        subprocess.run([
            "git", "config", "--local", "credential.helper", 
            f"store --file={credentials_file}"
        ], cwd=repo_path, check=True)

def get_git_remote_url(repo_path: str, remote_name: str) -> str | None:
    """Get URL for a specific git remote.
    @param repo_path: The path to the git repository
    @param remote_name: The name of the remote
    @return: The URL of the remote or None if not found
    """
    try:
        result = subprocess.run(
            ["git", "remote", "get-url", remote_name],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None

def get_all_git_remotes(repo_path: str) -> dict[str, str]:
    """Get all git remotes with their URLs.
    @param repo_path: The path to the git repository
    @return: A dictionary mapping remote names to their URLs
    """
    try:
        # Get all remote names
        result = subprocess.run(
            ["git", "remote"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        remote_names = result.stdout.strip().split('\n')
        
        # Get URLs for each remote
        remotes = {}
        for remote_name in remote_names:
            if remote_name:  # Skip empty lines
                url = get_git_remote_url(repo_path, remote_name)
                if url:
                    remotes[remote_name] = url
        
        return remotes
    except subprocess.CalledProcessError:
        return {}

def check_cache_overleaf_git_config_valid(overleaf_id: str, gitlab_paths: list[str], cache_dir: str) -> bool:
    """
    Check if git config in cache is valid:
    - origin remote should point to https://git.overleaf.com/<overleaf_id>
    - backup0, backup1, ... remotes should match gitlab_paths
    @param overleaf_id: The Overleaf project ID
    @param gitlab_paths: The list of GitLab repository paths
    @param cache_dir: The cache directory path
    @return: True if the config is valid, False otherwise
    """
    repo_path = os.path.join(cache_dir, f"overleaf_{overleaf_id}")
    
    # Check if repo exists and is a git repo
    if not check_cache_overleaf_git_existence(overleaf_id, cache_dir):
        print(f"Git repository not found in {repo_path}")
        return False
    
    # Get all current remotes
    current_remotes = get_all_git_remotes(repo_path)
    
    # Check origin remote
    expected_origin = f"https://git.overleaf.com/{overleaf_id}"
    if "origin" not in current_remotes:
        print(f"Missing origin remote in {repo_path}")
        return False
    
    if current_remotes["origin"] != expected_origin:
        print(f"Origin remote mismatch:")
        print(f"  Expected: {expected_origin}")
        print(f"  Found: {current_remotes['origin']}")
        return False
    
    # Check backup remotes
    expected_backups = {}
    for i, gitlab_path in enumerate(gitlab_paths):
        backup_name = f"backup{i}"
        expected_url = f"ssh://{gitlab_path}"
        expected_backups[backup_name] = expected_url
    
    # Verify each expected backup remote exists and has correct URL
    for backup_name, expected_url in expected_backups.items():
        if backup_name not in current_remotes:
            print(f"Missing backup remote '{backup_name}' in {repo_path}")
            return False
        
        if current_remotes[backup_name] != expected_url:
            print(f"Backup remote '{backup_name}' URL mismatch:")
            print(f"  Expected: {expected_url}")
            print(f"  Found: {current_remotes[backup_name]}")
            return False
    
    # Check for unexpected remotes (optional warning)
    expected_remotes = set(["origin"] + list(expected_backups.keys()))
    unexpected_remotes = set(current_remotes.keys()) - expected_remotes
    if unexpected_remotes:
        print(f"Warning: Unexpected remotes found: {unexpected_remotes}")

    print(f"Git config valid for {overleaf_id}")
    return True

def setup_git_remotes(overleaf_id: str, gitlab_paths: list[str], cache_dir: str) -> bool:
    """Setup/update git remotes to match expected configuration.
    @param overleaf_id: The Overleaf project ID
    @param gitlab_paths: The list of GitLab repository paths
    @param cache_dir: The cache directory path
    @return: True if the setup was successful, False otherwise
    """
    repo_path = os.path.join(cache_dir, f"overleaf_{overleaf_id}")
    
    # Ensure git repo exists
    if not check_cache_overleaf_git_existence(overleaf_id, cache_dir):
        print(f"Creating git repository in {repo_path}")
        mk_cache_overleaf_git_dir(overleaf_id, cache_dir)
    
    try:
        # Set/update origin remote
        origin_url = f"https://git.overleaf.com/{overleaf_id}"
        current_remotes = get_all_git_remotes(repo_path)
        
        if "origin" in current_remotes:
            subprocess.run([
                "git", "remote", "set-url", "origin", origin_url
            ], cwd=repo_path, check=True, capture_output=True)
            print(f"✓ Updated origin remote: {origin_url}")
        else:
            subprocess.run([
                "git", "remote", "add", "origin", origin_url
            ], cwd=repo_path, check=True, capture_output=True)
            print(f"✓ Added origin remote: {origin_url}")
        
        # Remove old backup remotes
        current_remotes = get_all_git_remotes(repo_path)
        for remote_name in current_remotes:
            if remote_name.startswith("backup"):
                subprocess.run([
                    "git", "remote", "remove", remote_name
                ], cwd=repo_path, check=True, capture_output=True)
                print(f"Removed old backup remote: {remote_name}")
        
        # Add new backup remotes
        for i, gitlab_path in enumerate(gitlab_paths):
            backup_name = f"backup{i}"
            backup_url = f"ssh://{gitlab_path}"
            subprocess.run([
                "git", "remote", "add", backup_name, backup_url
            ], cwd=repo_path, check=True, capture_output=True)
            print(f"✓ Added backup remote {backup_name}: {backup_url}")
        
        print(f"✓ Git remotes configured for {overleaf_id}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error setting up git remotes: {e}")
        return False

def sync_repositories(overleaf_id: str, cache_dir: str, verbose: bool = False) -> bool:
    """Sync repositories: git remote update -> pull from overleaf -> push to backups
    @param overleaf_id: The Overleaf project ID
    @param cache_dir: The cache directory path
    @param verbose: Whether to enable verbose output
    @return: True if the sync was successful, False otherwise
    """
    repo_path = os.path.join(cache_dir, f"overleaf_{overleaf_id}")
    
    if not check_cache_overleaf_git_existence(overleaf_id, cache_dir):
        print(f"Error: Git repository not found in {repo_path}")
        return False
    
    try:
        # 1. git remote update
        if verbose:
            print(f"Updating remotes for {overleaf_id}...")
        subprocess.run([
            "git", "remote", "update"
        ], cwd=repo_path, check=True, capture_output=not verbose)
        print("Remote update completed")
        
        # 2. git pull origin (try main and master)
        if verbose:
            print(f"Pulling from Overleaf for project {overleaf_id}...")
        
        pulled = False
        for branch in ["main", "master"]:
            try:
                subprocess.run([
                    "git", "pull", "origin", branch
                ], cwd=repo_path, check=True, capture_output=not verbose)
                print(f"✓ Successfully pulled from origin/{branch}")
                pulled = True
                break
            except subprocess.CalledProcessError:
                if verbose:
                    print(f"Failed to pull from origin/{branch}, trying next...")
                continue
        
        if not pulled:
            print("Error: Could not pull from origin (tried main and master)")
            return False
        
        # 2.5. Fetch tags from origin (immer aktiviert)
        if verbose:
            print("Fetching tags from Overleaf...")
        try:
            subprocess.run([
                "git", "fetch", "origin", "--tags"
            ], cwd=repo_path, check=True, capture_output=not verbose)
            print("Tags fetched from origin")
        except subprocess.CalledProcessError as e:
            print(f"Warning: Could not fetch tags from origin: {e}")
        
        # 3. Push to backup remotes (seriell)
        current_remotes = get_all_git_remotes(repo_path)
        backup_remotes = [name for name in current_remotes.keys() if name.startswith('backup')]
        
        if not backup_remotes:
            print("Warning: No backup remotes found")
            return True
        
        # Get current branch
        try:
            result = subprocess.run([
                "git", "rev-parse", "--abbrev-ref", "HEAD"
            ], cwd=repo_path, capture_output=True, text=True, check=True)
            current_branch = result.stdout.strip()
        except subprocess.CalledProcessError:
            current_branch = "main"  # fallback
        
        # Push to each backup remote serially
        for remote in sorted(backup_remotes):  # Sort for consistent order
            if verbose:
                print(f"Pushing to {remote} ({current_remotes[remote]})...")
            
            try:
                # Push current branch
                subprocess.run([
                    "git", "push", remote, current_branch
                ], cwd=repo_path, check=True, capture_output=not verbose)
                print(f"✓ Successfully pushed branch {current_branch} to {remote}")
                
                # Push tags (immer aktiviert)
                subprocess.run([
                    "git", "push", remote, "--tags"
                ], cwd=repo_path, check=True, capture_output=not verbose)
                print(f"✓ Successfully pushed tags to {remote}")
                
            except subprocess.CalledProcessError as e:
                print(f"✗ Failed to push to {remote}: {e}")
                # Continue with other remotes even if one fails
                continue

        print(f"Sync completed for {overleaf_id}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"Error during sync: {e}")
        return False

def backup_overleaf_project(overleaf_id: str, gitlab_paths: list[str], cache_dir: str, clean: bool, verbose: bool = False) -> bool:
    """Complete backup workflow for a single Overleaf project
    @param overleaf_id: The Overleaf project ID
    @param gitlab_paths: The list of GitLab repository paths
    @param cache_dir: The cache directory path
    @param clean: Whether to clean the cache after backup
    @param verbose: Whether to enable verbose output
    @return: True if the backup was successful, False otherwise
    """
    print(f"\n{'='*60}")
    print(f"Starting backup for Overleaf project: {overleaf_id}")
    print(f"GitLab paths: {gitlab_paths}")
    print(f"{'='*60}")
    
    # 1. Setup git remotes
    if not setup_git_remotes(overleaf_id, gitlab_paths, cache_dir):
        print(f"Failed to setup git remotes for {overleaf_id}")
        return False
    
    # 2. Validate configuration
    if not check_cache_overleaf_git_config_valid(overleaf_id, gitlab_paths, cache_dir):
        print(f"Git configuration invalid for {overleaf_id}")
        return False
    
    # 3. Sync repositories
    if not sync_repositories(overleaf_id, cache_dir, verbose):
        print(f"Failed to sync repositories for {overleaf_id}")
        return False
    
    print(f"Backup completed successfully for {overleaf_id}")

    if clean:
        repo_path = os.path.join(cache_dir, f"overleaf_{overleaf_id}")
        print(f"Cleaning up cache directory: {repo_path}")
        subprocess.run(["rm", "-rfd", repo_path], check=True)
    return True

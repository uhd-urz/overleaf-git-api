import os
import subprocess
from typing import Optional

def get_git_remote_url(repo_path: str, remote_name: str) -> Optional[str]:
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
        result = subprocess.run(
            ["git", "remote"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            check=True
        )
        remote_names = result.stdout.strip().split('\n')
        
        remotes = {}
        for name in remote_names:
            if url := get_git_remote_url(repo_path, name):
                remotes[name] = url
        return remotes
    except subprocess.CalledProcessError:
        return {}

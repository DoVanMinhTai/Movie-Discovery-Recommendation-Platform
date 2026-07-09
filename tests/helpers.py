"""
Helper functions for property-based testing of env-centralization feature.
"""
import os
import subprocess
from pathlib import Path
from typing import List, Tuple, Dict, Any

import yaml
from dotenv import dotenv_values


def parse_env_file(path: str) -> List[Tuple[str, str]]:
    """
    Parse an env file and return list of (key, value) tuples.
    Preserves order and duplicates (if any).
    
    Args:
        path: Relative or absolute path to .env file
        
    Returns:
        List of (key, value) tuples in order of appearance
    """
    env_path = Path(path)
    if not env_path.exists():
        return []
    
    result = []
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and comments
            if not line or line.startswith('#'):
                continue
            # Parse KEY=VALUE format
            if '=' in line:
                key, _, value = line.partition('=')
                result.append((key.strip(), value.strip()))
    
    return result


def parse_env_keys(path: str) -> List[str]:
    """
    Parse an env file and return list of keys only.
    
    Args:
        path: Relative or absolute path to .env file
        
    Returns:
        List of environment variable keys
    """
    return [key for key, _ in parse_env_file(path)]


def parse_env_values(path: str) -> List[str]:
    """
    Parse an env file and return list of values only.
    
    Args:
        path: Relative or absolute path to .env file
        
    Returns:
        List of environment variable values
    """
    return [value for _, value in parse_env_file(path)]


def parse_docker_compose(path: str) -> Dict[str, Any]:
    """
    Parse docker-compose.yml file using PyYAML.
    
    Args:
        path: Relative or absolute path to docker-compose.yml
        
    Returns:
        Parsed YAML as dictionary
    """
    compose_path = Path(path)
    if not compose_path.exists():
        return {}
    
    with open(compose_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f) or {}


def get_tracked_python_files(dirs: List[str]) -> List[str]:
    """
    Get list of git-tracked .py files in specified directories.
    
    Args:
        dirs: List of directory paths relative to repo root
        
    Returns:
        List of absolute paths to tracked Python files
    """
    result = []
    for dir_path in dirs:
        try:
            # Get all git-tracked files in this directory (without glob pattern)
            output = subprocess.check_output(
                ['git', 'ls-files', dir_path],
                text=True,
                stderr=subprocess.DEVNULL
            )
            files = [line.strip() for line in output.split('\n') if line.strip()]
            # Filter for .py files in Python
            py_files = [f for f in files if f.endswith('.py')]
            # Convert to absolute paths
            result.extend([os.path.abspath(f) for f in py_files])
        except (subprocess.CalledProcessError, FileNotFoundError):
            # Git command failed or git not available - skip this directory
            continue
    
    return result


def get_tracked_files(dir_path: str) -> List[str]:
    """
    Get list of all git-tracked files in specified directory.
    
    Args:
        dir_path: Directory path relative to repo root
        
    Returns:
        List of absolute paths to tracked files
    """
    try:
        output = subprocess.check_output(
            ['git', 'ls-files', dir_path],
            text=True,
            stderr=subprocess.DEVNULL
        )
        files = [line.strip() for line in output.split('\n') if line.strip()]
        return [os.path.abspath(f) for f in files]
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Git command failed or git not available
        return []

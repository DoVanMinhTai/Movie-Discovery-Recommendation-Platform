"""
Environment Configuration Loader
Loads environment variables from parent directory's .env file
"""
import os
from pathlib import Path
from dotenv import load_dotenv

def load_env():
    """
    Load environment variables from parent directory
    Supports both .env.dev and .env.prod based on ENV variable
    """
    # Get current file's directory
    current_dir = Path(__file__).resolve().parent
    
    # Get project root (parent directory)
    project_root = current_dir.parent
    
    # Determine which env file to load
    env_mode = os.getenv('ENV', 'dev')  # default to dev
    env_file = project_root / f'.env.{env_mode}'
    
    # Fallback to .env if specific file doesn't exist
    if not env_file.exists():
        env_file = project_root / '.env'
    
    # Load the environment file
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from: {env_file}")
    else:
        print(f"⚠️ No environment file found at: {env_file}")
        print(f"   Searched in: {project_root}")

# Auto-load when imported
load_env()

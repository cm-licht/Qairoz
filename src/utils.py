import json
import os

def load_config(path):
    """Loads the JSON configuration file."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Config file not found at {path}")
    
    with open(path, 'r') as f:
        return json.load(f)

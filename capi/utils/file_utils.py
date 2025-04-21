import os
import fnmatch
from pathlib import Path

def get_gitignore_patterns(root_path: str) -> list[str]:
    patterns = []
    gitignore_path = os.path.join(root_path, '.gitignore')
    
    if os.path.exists(gitignore_path):
        with open(gitignore_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    return patterns

def should_ignore(path: str, patterns: list[str]) -> bool:
    path = Path(path)
    
    # Check against base patterns first
    base_name = path.name
    if any(p in base_name for p in ['__pycache__', '.pyc', '.git', '.DS_Store']):
        return True
        
    # Convert path to posix format for consistent matching
    posix_path = path.as_posix()
    
    for pattern in patterns:
        pattern = pattern.rstrip('/')
        
        # Handle pattern variations
        if pattern.startswith('/'):
            if fnmatch.fnmatch(posix_path, pattern[1:]):
                return True
        elif pattern.startswith('**/'):
            if fnmatch.fnmatch(posix_path, pattern[3:]):
                return True
        else:
            if fnmatch.fnmatch(base_name, pattern):
                return True
            if fnmatch.fnmatch(posix_path, f'**/{pattern}'):
                return True
            
    return False

def is_binary_file(file_path: str, sample_size: int = 1024) -> bool:
    try:
        with open(file_path, 'rb') as f:
            sample = f.read(sample_size)
            
        # Consider a file as binary if it contains null bytes
        if b'\x00' in sample:
            return True
            
        # Check for high concentration of non-text bytes
        text_chars = bytes(range(32, 127)) + b'\n\r\t\f\b'
        non_text = sum(1 for byte in sample if byte not in text_chars)
        
        return non_text / len(sample) > 0.3
        
    except Exception:
        return True

def get_file_contents(file_path: str) -> str | None:
    try:
        # Read file in binary mode first to handle potential encoding issues
        with open(file_path, 'rb') as f:
            content = f.read()
            
        # Try to decode with utf-8
        try:
            return content.decode('utf-8')
        except UnicodeDecodeError:
            # If utf-8 fails, try with a more permissive encoding
            return content.decode('latin-1')
            
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return None
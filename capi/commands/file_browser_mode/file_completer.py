from prompt_toolkit.completion import Completer, Completion
import os
from pathlib import Path

class FileCompleter(Completer):
    def __init__(self):
        self.prompt_dir = os.getcwd()
        
    def should_ignore(self, path: str) -> bool:
        ignore_patterns = {
            '.git', '__pycache__', 'venv', 'node_modules', 
            '.pytest_cache', '.vscode', '.idea', 'build',
            'dist', '*.pyc', '*.pyo', '*.pyd', '.DS_Store',
            '.env', '.venv', '*capi.egg-info'
        }
        
        path_parts = Path(path).parts
        return any(
            any(part.startswith(pattern.strip('*')) for part in path_parts)
            for pattern in ignore_patterns
        )

    def is_binary(self, path: str) -> bool:
        try:
            with open(path, 'tr') as check:
                check.read(1024)
                return False
        except:
            return True

    def get_files(self):
        files = []
        for prompt, _, filenames in os.walk(self.prompt_dir):
            for filename in filenames:
                full_path = os.path.join(prompt, filename)
                rel_path = os.path.relpath(full_path, self.prompt_dir)
                
                if not self.should_ignore(rel_path) and not self.is_binary(full_path):
                    files.append(rel_path)
        return sorted(files)

    def get_completions(self, document, complete_event):
        text = document.text.lower()
        
        # Only show completions if the line starts with 'file '
        if not text.startswith('file '):
            return
            
        # Get the actual file part after 'file '
        word = text[5:]
        
        for file_path in self.get_files():
            filename = os.path.basename(file_path)
            if word in filename.lower():
                yield Completion(
                    file_path,
                    start_position=-len(word),
                    display=file_path
                )
import os
from typing import Dict, List, Union
from .file_utils import should_ignore, is_binary_file

def generate_json_structure(startpath: str, ignore_patterns: List[str], always_ignore: List[str]) -> Dict:
    structure = {"files": [], "directories": {}}
    
    for item in os.listdir(startpath):
        item_path = os.path.join(startpath, item)
        rel_path = os.path.relpath(item_path, startpath)
        
        if not should_ignore(rel_path, ignore_patterns + always_ignore):
            if os.path.isfile(item_path):
                if not is_binary_file(item_path):
                    structure["files"].append(item)
            elif os.path.isdir(item_path):
                structure["directories"][item] = generate_json_structure(
                    item_path, ignore_patterns, always_ignore
                )
    
    if not structure["files"]:
        del structure["files"]
    if not structure["directories"]:
        del structure["directories"]
    
    return structure

def generate_tree_structure(startpath: str, ignore_patterns: List[str], always_ignore: List[str]) -> str:
    lines = []
    prefix_map = {"├── ": "│   ", "└── ": "    "}
    
    def add_item(path: str, prefix: str = "") -> None:
        items = sorted(os.listdir(path))
        items = [item for item in items 
                if not should_ignore(os.path.relpath(os.path.join(path, item), startpath), 
                                   ignore_patterns + always_ignore)]
        
        for i, item in enumerate(items):
            item_path = os.path.join(path, item)
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            
            lines.append(f"{prefix}{connector}{item}")
            
            if os.path.isdir(item_path):
                lines[-1] += "/"
                next_prefix = prefix + prefix_map[connector]
                add_item(item_path, next_prefix)
    
    lines.append(os.path.basename(startpath) + "/")
    add_item(startpath)
    return "\n".join(lines)

def generate_directory_structure(startpath: str, 
                               ignore_patterns: List[str], 
                               always_ignore: List[str], 
                               format: str = "tree") -> Union[Dict, str]:
    if format == "json":
        return generate_json_structure(startpath, ignore_patterns, always_ignore)
    structure = generate_tree_structure(startpath, ignore_patterns, always_ignore)
    return (
        '<project-structure description="This represents the structure of the directory. '
        'Use this tag to ensure proper referencing of files, functions, etc...">\n    '
        f'{structure}\n'
        '</project-structure>'
    )
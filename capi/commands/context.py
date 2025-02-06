import click
import os
import json
import pyperclip
from pathlib import Path
from ..utils.file_utils import (
    get_gitignore_patterns,
    get_file_contents,
    is_binary_file,
    should_ignore
)
from ..utils.structure_utils import generate_directory_structure

def copy_code_context(src_dir: str, include_files: bool, include_structure: bool, 
                     include_context: bool, format: str = "tree") -> None:
    """Generate project context based on specified flags and copy to clipboard."""
    if src_dir == '.':
        src_dir = os.getcwd()
    
    output_parts = []
    
    # Get ignore patterns
    ignore_patterns = get_gitignore_patterns(src_dir)
    always_ignore = ['venv', '__pycache__', '.git', 'node_modules', '.gitignore', 'capi.egg-info']
    
    # Add files section if requested
    if include_files:
        files_content = []
        all_files = []
        
        for root, dirs, files in os.walk(src_dir):
            dirs[:] = [d for d in dirs if not should_ignore(
                os.path.relpath(os.path.join(root, d), src_dir), 
                ignore_patterns + always_ignore
            )]
            
            for file in files:
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, src_dir)
                if not should_ignore(rel_path, ignore_patterns + always_ignore):
                    if not is_binary_file(filepath):
                        all_files.append(rel_path)
        
        all_files.sort()
        
        files_content.append("<project-files>")
        for file in all_files:
            full_path = os.path.join(src_dir, file)
            content = get_file_contents(full_path)
            if content is not None:
                files_content.append(f"```{file}\n{content}\n```")
            else:
                click.echo(f"Error reading file: {file}", err=True)
        files_content.append("</project-files>")
        
        output_parts.append("\n".join(files_content))
        click.echo(f"Processed {len(all_files)} files.")
    
    # Add structure section if requested
    if include_structure:
        structure = generate_directory_structure(src_dir, ignore_patterns, always_ignore, format="tree")
        structure_content = [
            "\n<project-structure>",
            structure,
            "</project-structure>"
        ]
        output_parts.append("\n".join(structure_content))
        click.echo("Added project structure.")
    
    # Add context from ctx.xml if requested
    if include_context:
        ctx_path = Path(src_dir) / 'prompting' / 'cli' / 'ctx.xml'
        if ctx_path.exists():
            try:
                with open(ctx_path, 'r', encoding='utf-8') as f:
                    context_content = f.read()
                output_parts.append(f"\n<context>\n{context_content}\n</context>")
                click.echo("Added context from ctx.xml")
            except Exception as e:
                click.echo(f"Error reading ctx.xml: {e}", err=True)
        else:
            click.echo("Warning: ctx.xml not found at prompting/cli/ctx.xml", err=True)
    
    # Join all parts and copy to clipboard
    final_output = "\n\n".join(output_parts)
    pyperclip.copy(final_output)
    
    click.echo("Content has been copied to clipboard!")
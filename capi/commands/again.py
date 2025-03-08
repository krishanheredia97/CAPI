import os
import json
import click
import pyperclip
from ..utils.file_utils import get_file_contents, get_gitignore_patterns
from ..utils.structure_utils import generate_directory_structure

def copy_again(prompt_dir):
    """Copy last selection again."""
    if prompt_dir == '.':
        prompt_dir = os.getcwd()

    selection_file = os.path.join(prompt_dir, 'prompting', 'cli', 'last_selection.json')
    
    if not os.path.exists(selection_file):
        click.echo("Error: No previous selection found. Please run init first.")
        return

    with open(selection_file, 'r') as f:
        last_selection = json.load(f)

    if not last_selection.get("files"):
        click.echo("Error: No previous selection found. Please use ui first.")
        return

    output_parts = []
    
    # Add files section
    files_content = ["<project-files>"]
    for file in sorted(last_selection["files"]):
        full_path = os.path.join(prompt_dir, file)
        content = get_file_contents(full_path)
        if content is not None:
            files_content.append(f"```{file}\n{content}\n```")
    files_content.append("</project-files>")
    output_parts.append("\n".join(files_content))

    # Add structure section
    ignore_patterns = get_gitignore_patterns(prompt_dir)
    always_ignore = ['venv', '__pycache__', '.git', 'node_modules', '.gitignore', 'capi.egg-info']
    structure = generate_directory_structure(prompt_dir, ignore_patterns, always_ignore)
    structure_content = [
        "\n<project-structure description=\"This represents the structure of the directory. Use this tag to ensure proper referencing of files, functions, etc...\">\n    ",
        json.dumps(structure, indent=4),
        "</project-structure>"
    ]
    output_parts.append("\n".join(structure_content))

    # Add context from ctx.xml if it exists
    ctx_path = os.path.join(prompt_dir, 'prompting', 'cli', 'ctx.xml')
    if os.path.exists(ctx_path):
        try:
            with open(ctx_path, 'r', encoding='utf-8') as f:
                context_content = f.read()
            output_parts.append(f"\n<context>\n{context_content}\n</context>")
        except Exception as e:
            click.echo(f"Warning: Could not read ctx.xml: {e}", err=True)

    # Join all parts and copy to clipboard
    final_output = "\n\n".join(output_parts)
    pyperclip.copy(final_output)
    
    click.echo(f"Recopied {len(last_selection['files'])} files from last selection!")
import os
import json
import click

def init_cli(root_dir):
    """Initialize CLI configuration."""
    if root_dir == '.':
        root_dir = os.getcwd()

    # Create prompting/cli directory
    cli_dir = os.path.join(root_dir, 'prompting', 'cli')
    os.makedirs(cli_dir, exist_ok=True)

    # Create empty last_selection.json
    selection_file = os.path.join(cli_dir, 'last_selection.json')
    if not os.path.exists(selection_file):
        with open(selection_file, 'w') as f:
            json.dump({"files": []}, f)
        click.echo(f"Initialized CLI configuration in {cli_dir}")
    else:
        click.echo(f"CLI configuration already exists in {cli_dir}")
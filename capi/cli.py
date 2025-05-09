import click
import os

@click.group()
def cli():
    """CLI tool for managing project context and structure."""
    pass

@cli.command()
@click.option('--files', is_flag=True, help='Include file contents')
@click.option('--str', 'structure', is_flag=True, help='Include project structure')
@click.option('--ctx', is_flag=True, help='Include context from ctx.xml')
@click.option('--format', type=click.Choice(['tree', 'json']), default='tree', help='Structure format')
def code(files, structure, ctx, format):
    """Copy project context based on specified flags. If no flags, includes everything."""
    from .commands.context import copy_code_context
    if not any([files, structure, ctx]):
        files = structure = ctx = True
    
    copy_code_context(
        src_dir='.',
        include_files=files,
        include_structure=structure,
        include_context=ctx,
        format=format
    )

@cli.command()
@click.option('--src', type=click.Path(exists=True), help='Source directory (defaults to current directory)')
@click.option('--include-structure', type=int, default=1, help='Include project structure (1=yes, 0=no)')
def ui(src, include_structure):
    """Open UI selector"""
    from .commands.ui import open_ui
    if not src:
        src = '.'
    open_ui(src, include_structure)

@cli.command()
@click.option('--src', type=click.Path(exists=True), help='Source directory (defaults to current directory)')
def init(src):
    """Initialize CLI configuration"""
    from .commands.init import init_cli
    if not src:
        src = '.'
    init_cli(src)

@cli.command()
@click.option('--src', type=click.Path(exists=True), help='Source directory (defaults to current directory)')
def again(src):
    """Recopy last selection"""
    from .commands.again import copy_again
    if not src:
        src = '.'
    copy_again(src)

@cli.command()
@click.argument('agent_id', required=False, default='coder')
def ask(agent_id):
    """Ask a question using a specific agent"""
    from .commands.ask import handle_ask
    handle_ask(agent_id)

@cli.command()
def design():
    """Enter interactive prompt design mode"""
    from .commands.designer_mode.design import design_prompt
    design_prompt()

@cli.command()
def pdm():
    """Enter interactive prompt design mode (alias for design)"""
    from .commands.designer_mode.design import design_prompt
    design_prompt()

@cli.command()
@click.argument("command", required=True)
def term(command):
    """Execute a command and copy its terminal output to the clipboard within XML tags."""
    from .commands.term import copy_terminal_content
    copy_terminal_content(command)

@cli.command()
@click.argument('query', type=str, required=False)
@click.option('--questions', type=int, required=True, help='Number of questions to extract')
@click.option('--verbose', is_flag=True, help='Print full prompts for debugging')
@click.option('--paste', is_flag=True, help='Use clipboard content as query')
def query(query, questions, verbose, paste):
    """Execute a complex query workflow using multiple agents."""
    from .commands.query import handle_query
    handle_query(query, questions, verbose, paste)

@cli.command()
def file():
    """Browse and copy content of project files."""
    from .commands.file_browser_mode.file import handle_file
    handle_file()

def main():
    cli()
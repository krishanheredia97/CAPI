import click
import subprocess
import os

def capture_command_output(command):
    """
    Capture the output (stdout and stderr) of a given command.
    """
    try:
        # Execute the command and capture both stdout and stderr
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            check=True,
        )
        # Combine stdout and stderr into a single output
        output = result.stdout + result.stderr
    except subprocess.CalledProcessError as e:
        # If the command fails, capture the error output
        output = e.stdout + e.stderr
    except Exception as e:
        # Handle other exceptions (e.g., invalid command)
        output = f"Failed to execute command: {str(e)}"
    return output.strip()

def copy_terminal_content(command):
    """
    Execute the given command, capture its output, and write it to the specified file within XML tags.
    Overwrites the file content instead of appending.
    """
    # Capture the command output
    terminal_content = capture_command_output(command)
    
    # Wrap the content in the specified XML tags
    xml_content = f'<terminal description="This is the content of my terminal window">\n{terminal_content}\n</terminal>'
    
    # Define the file path
    file_path = "prompting/cli/terminal_error.xml"
    
    # Ensure the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Write the content to the file (overwrite if the file exists)
    with open(file_path, "w") as file:
        file.write(xml_content)
    
    click.echo(f"Command output written to {file_path} within XML tags (overwritten).")

@click.command()
@click.argument("command", required=True)
def term(command):
    """
    Execute a command and write its terminal output to a file within XML tags.
    Overwrites the file content instead of appending.

    Example:
    capi term "py main.py"
    """
    copy_terminal_content(command)
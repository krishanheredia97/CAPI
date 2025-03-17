from typing import Optional
import os
import click
import pyperclip
from dotenv import load_dotenv
from ..utils.clipboard_utils import get_clipboard_content
from ..commands.agent_systems.workflow_processor import execute_workflow

def handle_query(query, questions, verbose, paste):
    """Handle complex query workflow using multiple agents"""
    # Load environment variables from .env file if it exists
    load_dotenv()
    
    # Set verbose mode as environment variable for other components
    if verbose:
        os.environ["VERBOSE"] = "1"
    
    if paste:
        query = pyperclip.paste()
    
    if not query:
        click.secho("Error: No query provided. Please provide a query or use --paste.", fg='red')
        return
    
    # Try multiple possible API keys
    api_key = os.environ.get("DEEPINFRA_API_TOKEN") or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        click.secho("Error: No API token found. Please set DEEPINFRA_API_TOKEN or OPENAI_API_KEY environment variable.", fg='red')
        return
    
    if verbose:
        click.secho(f"Using API key (first 4 chars): {api_key[:4]}...", fg='cyan')
    
    # Execute the query_processor workflow
    parameters = {"num_questions": questions}
    try:
        execute_workflow("query_processor", query, api_key, parameters, verbose)
    except Exception as e:
        click.secho(f"Workflow execution failed: {str(e)}", fg='red')
        if verbose:
            import traceback
            click.secho(traceback.format_exc(), fg='red')
from typing import Optional
import os
import click
from dotenv import load_dotenv
from ..utils.clipboard_utils import get_clipboard_content
from .agent_systems.workflow_processor import execute_workflow

def handle_query(query: Optional[str], questions: int, verbose: bool, paste: bool):
    """Execute a complex query workflow using configured agentic systems"""
    load_dotenv()
    api_key = os.getenv("DEEPINFRA_API_TOKEN")
    
    if not api_key:
        click.secho("DEEPINFRA_API_TOKEN not set", fg='red')
        return

    # Handle clipboard input
    if not query or paste:
        try:
            query = get_clipboard_content()
            if not query.strip():
                click.secho("Error: Clipboard is empty", fg='red')
                return
        except Exception as e:
            click.secho(f"Error: {str(e)}", fg='red')
            return

    # Execute the workflow
    try:
        execute_workflow(
            workflow_name="query_processor",
            user_input=query,
            api_key=api_key,
            parameters={"num_questions": questions},
            verbose=verbose
        )
    except Exception as e:
        click.secho(f"Workflow execution failed: {str(e)}", fg='red')
        raise
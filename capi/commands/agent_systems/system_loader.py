import json
import os
from pathlib import Path
from typing import Dict, Any
import click
from ...utils.llm_api_caller import LLMApiCaller

def load_workflow(workflow_name: str) -> Dict[str, Any]:
    """Load and validate a workflow from directory with config.json"""
    workflow_dir = Path(f"capi/commands/agent_systems/workflows/{workflow_name}")
    config_path = workflow_dir / "config.json"
    
    if not workflow_dir.is_dir():
        raise FileNotFoundError(f"Workflow directory not found: {workflow_dir}")
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found in workflow directory: {config_path}")
    
    try:
        with open(config_path, 'r') as f:
            workflow = json.load(f)
        
        # Add directory information to workflow config
        workflow['_workflow_dir'] = str(workflow_dir.resolve())
        validate_workflow(workflow)
        return workflow
        
    except Exception as e:
        click.secho(f"Error loading workflow: {str(e)}", fg='red')
        raise

def validate_workflow(workflow: Dict[str, Any]):
    """Validate workflow structure"""
    required_keys = ["id", "name", "flow"]
    node_types = ["soft_agent", "hard_agent", "parser", "function", "human"]
    
    # Validate top-level structure
    for key in required_keys:
        if key not in workflow:
            raise ValueError(f"Missing required workflow key: {key}")
    
    # Validate nodes
    node_ids = set()
    workflow_dir = Path(workflow["_workflow_dir"])
    
    for node in workflow["flow"]:
        # Check node ID uniqueness
        if node["id"] in node_ids:
            raise ValueError(f"Duplicate node ID: {node['id']}")
        node_ids.add(node["id"])
        
        # Validate node type
        if node["node_type"] not in node_types:
            raise ValueError(f"Invalid node type '{node['node_type']}' in node {node['id']}")
        
        # Validate parser configuration
        if node["node_type"] == "parser":
            if "parser_type" not in node:
                raise ValueError(f"Parser node {node['id']} missing 'parser_type'")
            if "config" not in node or "structure" not in node["config"]:
                raise ValueError(f"Parser node {node['id']} missing required config structure")
        
        # Validate function configuration
        if node["node_type"] == "function" and "function_type" not in node.get("config", {}):
            raise ValueError(f"Function node {node['id']} missing 'function_type' in config")
        
        # Validate input sources exist in context
        for source in node.get("input_sources", []):
            if not any([source.startswith(f"{nid}.") for nid in node_ids]) and source != "workflow.input":
                raise ValueError(f"Invalid input source '{source}' in node {node['id']}")
        
        # Validate prompt files exist for agent nodes
        if node["node_type"] in ["soft_agent", "hard_agent"]:
            if "prompt_file" not in node:
                raise ValueError(f"Agent node {node['id']} missing 'prompt_file'")
            
            prompt_path = workflow_dir / node["prompt_file"]
            if not prompt_path.exists():
                raise ValueError(f"Prompt file not found for node {node['id']}: {prompt_path}")

def initialize_agent(node: Dict[str, Any], api_key: str, workflow_dir: str) -> LLMApiCaller:
    """Create LLMApiCaller instance with workflow-relative paths"""
    prompt_path = Path(workflow_dir) / node['prompt_file']
    
    if not prompt_path.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
    
    with open(prompt_path, 'r') as f:
        system_prompt = f.read()
    
    return LLMApiCaller(
        api_key=api_key,
        model=node["model"],
        system_prompt=system_prompt,
        temperature=0.7 if node["node_type"] == "soft_agent" else 0.3
    )
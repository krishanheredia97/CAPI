import json
import click
from typing import Dict, Any, List
from ...utils.llm_api_caller import LLMApiCaller
from .system_loader import load_workflow, initialize_agent
from .parsers.json_extractor import extract_json_response

def execute_workflow(
    workflow_name: str,
    user_input: str,
    api_key: str,
    parameters: dict = None,
    verbose: bool = False
):
    try:
        workflow = load_workflow(workflow_name)
        context = {
            "workflow": {
                "input": user_input,
                "parameters": parameters or {}  
            }
        }
        context["workflow"]["flow"] = workflow["flow"]  
        current_node_id = workflow["flow"][0]["id"]
        node_map = {node["id"]: node for node in workflow["flow"]}
        
        # Set the workflow.input in the context before processing the nodes
        context["workflow"]["input"] = user_input
        
        while current_node_id:
            node = node_map[current_node_id]
            if verbose:
                click.secho(f"\n{'='*50}", fg='cyan')
                click.secho(f"Processing Node: {node['id']} ({node['node_type']})", fg='cyan', bold=True)
            
            # Process node based on type
            result = process_node(node, context, api_key, verbose)
            context.update(result)
            
            # Move to next node
            current_node_id = node["edges"][0] if node["edges"] else None
        
        # Find and return final output
        final_node = next((n for n in workflow["flow"] if n.get("final_output")), None)
        if final_node:
            click.secho("\nFinal Response:", fg='green', bold=True)
            click.secho(context[f"{final_node['id']}.output"], fg='white')
            
    except Exception as e:
        click.secho(f"\nWorkflow execution failed: {str(e)}", fg='red')
        raise

def process_node(node: Dict[str, Any], context: Dict[str, Any], api_key: str, verbose: bool) -> Dict[str, Any]:
    node_type = node["node_type"]

    if node_type in ["soft_agent", "hard_agent"]:
        return process_agent_node(node, context, api_key, verbose)
    elif node_type == "parser":
        return process_parser_node(node, context)
    elif node_type == "human":
        return process_human_node(node, context)
    elif node_type == "function":
        return process_function_node(node, context)
    else:
        raise ValueError(f"Unknown node type: {node_type}")

def process_agent_node(node: Dict[str, Any], context: Dict[str, Any], api_key: str, verbose: bool) -> Dict[str, Any]:
    agent = initialize_agent(node, api_key)
    input_data = get_input_data(node, context)

    # Add question count to the agent's prompt
    num_questions = context.get("workflow.parameters", {}).get("num_questions", 3)
    modified_prompt = f"{agent.system_prompt}\nGenerate exactly {num_questions} questions."
    agent.system_prompt = modified_prompt

    messages = [
        {"role": "system", "content": agent.system_prompt},
        {"role": "user", "content": input_data}
    ]

    if verbose:
        click.secho("\nInput Data:", fg='cyan')
        click.secho(input_data, fg='white')
        click.secho("\nSending to LLM...", fg='cyan')

    response = agent.get_response(messages)

    if verbose:
        click.secho("\nRaw Response:", fg='yellow')
        click.secho(response, fg='yellow')

    return {f"{node['id']}.output": response}

def process_parser_node(node: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Process a parser node"""
    input_data = get_input_data(node, context)
    parsed = extract_json_response(input_data, node["config"])
    
    # Ensure questions is a flat list of strings
    questions = parsed.get("questions", [])
    if questions and isinstance(questions[0], list):
        questions = questions[0]
    
    # Format questions as simple strings
    questions = [str(q) for q in questions]
    
    return {
        f"{node['id']}.output": parsed,
        f"{node['id']}.questions": questions
    }

def process_human_node(node: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Process human interaction node"""
    questions = get_input_data(node, context)
    
    # Ensure questions is a list of strings
    if isinstance(questions, str):
        questions = [questions]
    elif isinstance(questions, list) and questions and isinstance(questions[0], list):
        questions = questions[0]
    
    answers = []
    
    click.secho("\nPlease answer the following questions:", fg='yellow')
    for idx, question in enumerate(questions, 1):
        if isinstance(question, (list, dict)):
            continue  # Skip invalid question formats
        answer = click.prompt(f"\nQ{idx}: {question}")
        answers.append({
            "question": question,
            "answer": answer
        })
    
    return {f"{node['id']}.output": answers}

def process_function_node(node: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    """Process function node"""
    inputs = [get_input_data(node, context, source) for source in node["input_sources"]]
    
    if node["config"]["function_type"] == "key_value_merge":
        # Get questions and answers
        questions = inputs[0] if isinstance(inputs[0], list) else []
        answers = inputs[1] if isinstance(inputs[1], list) else []
        
        # Create merged QA pairs
        merged = []
        for q, a in zip(questions, answers):
            if isinstance(a, dict) and "question" in a and "answer" in a:
                merged.append({
                    "question": a["question"],
                    "answer": a["answer"]
                })
            else:
                # Handle the case where we have simple question-answer pairs
                merged.append({
                    "question": q,
                    "answer": a.get("answer", "") if isinstance(a, dict) else a
                })
        
        return {f"{node['id']}.output": merged}
    
    raise ValueError(f"Unknown function type: {node['config']['function_type']}")

def get_input_data(node: Dict[str, Any], context: Dict[str, Any], source: str = None) -> Any:
    sources = node["input_sources"] if not source else [source]
    input_data = []
    
    for src in sources:
        parts = src.split('.')
        if parts[0] == "workflow":
            # Handle workflow-level inputs
            current = context["workflow"]
            for part in parts[1:]:
                if isinstance(current, dict):
                    current = current.get(part)
                    if current is None:
                        raise ValueError(f"Missing workflow input '{src}' for node {node['id']}")
                else:
                    raise ValueError(f"Can't access '{part}' on non-dict value")
            input_data.append(current)
        else:
            # Handle node outputs
            current_node_id = parts[0]
            current = context.get(f"{current_node_id}.{parts[1]}" if len(parts) > 1 else f"{current_node_id}.output")
            if current is None:
                raise ValueError(f"Missing input source '{src}' for node {node['id']}")
            input_data.append(current)
    
    return "\n\n".join(map(str, input_data)) if len(input_data) > 1 else input_data[0]
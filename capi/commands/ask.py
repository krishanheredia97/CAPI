import os
import json
from dotenv import load_dotenv
from ..utils.llm_api_caller import LLMApiCaller
import click

def load_agents(json_path='prompting/cli/agents.json'):
    with open(json_path, 'r') as f:
        data = json.load(f)
    agents = {agent['id']: agent for agent in data['agents']}
    return agents

def handle_ask(agent_id):
    load_dotenv()
    api_key = os.getenv("DEEPINFRA_API_TOKEN")
    if not api_key:
        click.secho("DEEPINFRA_API_TOKEN environment variable is not set.", fg='red')
        return

    agents = load_agents()
    if agent_id not in agents:
        click.secho(f"Agent with ID '{agent_id}' not found. Using default agent 'Code Assistant'.", fg='yellow')
        agent_id = 'coder'
    
    agent = agents[agent_id]
    llm = LLMApiCaller(
        api_key=api_key,
        model=agent['model'],
        system_prompt=agent['system_prompt'],
        temperature=0.7
    )
    
    llm.interactive_session()
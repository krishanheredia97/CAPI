import click
from typing import List, Dict, Any

def sequential_qa(items: List[Any], config: Dict[str, Any] = None) -> List[Dict[str, str]]:
    """
    Collect answers for a list of questions/items sequentially
    Args:
        items: List of questions or items to present
        config: Additional configuration parameters
    Returns:
        List of question-answer pairs
    """
    if not items:
        return []
    
    click.secho("\n=== Human Interaction Required ===", fg='yellow')
    answers = []
    
    for idx, item in enumerate(items, 1):
        if isinstance(item, dict):
            question = item.get('question', str(item))
        else:
            question = str(item)
            
        answer = click.prompt(f"\nQ{idx}: {question}")
        answers.append({
            'question': question,
            'answer': answer
        })
    
    click.secho("=== Interaction Complete ===\n", fg='yellow')
    return answers

def validate_sequential_config(config: Dict[str, Any]):
    """Validate sequential QA configuration"""
    allowed_keys = ['instructions', 'retry_attempts']
    for key in config:
        if key not in allowed_keys:
            raise ValueError(f"Invalid config key for sequential QA: {key}")
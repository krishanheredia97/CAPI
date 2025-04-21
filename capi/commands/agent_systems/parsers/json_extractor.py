import json
import click
from jsonpath_ng import parse
from typing import Any, Dict

def extract_json_response(data: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract values from JSON data using configured paths
    Args:
        data: Raw JSON string from LLM response
        config: Extraction configuration from workflow JSON.
    Returns:
        Dictionary of extracted values
    """
    try:
        # Handle potential string cleaning
        data = data.strip()
        if data.startswith("```json"):
            data = data[7:]
        if data.endswith("```"):
            data = data[:-3]
        
        parsed_data = json.loads(data.strip())
    except json.JSONDecodeError as e:
        click.secho(f"Invalid JSON: {str(e)}", fg='red')
        raise
    
    results = {}
    
    for field_name, field_config in config.get('structure', {}).items():
        json_path = field_config['path']
        expected_type = field_config.get('type', 'auto')
        
        try:
            # Extract values using JSONPath
            expr = parse(json_path)
            matches = [match.value for match in expr.find(parsed_data)]
            
            # Handle type conversions
            if expected_type == 'list':
                # Ensure we have a flat list of strings
                if matches and isinstance(matches[0], list):
                    matches = matches[0]
                results[field_name] = [str(m) if isinstance(m, (list, dict)) else m for m in matches]
            elif expected_type == 'dict':
                results[field_name] = matches[0] if matches else {}
            elif expected_type == 'str':
                results[field_name] = str(matches[0]) if matches else ''
            else:  # auto-detect
                results[field_name] = matches[0] if len(matches) == 1 else matches
                
        except Exception as e:
            click.secho(f"Failed to extract '{field_name}': {str(e)}", fg='red')
            raise
    
    return results

def validate_extractor_config(config: Dict[str, Any]):
    """Validate JSON extractor configuration"""
    required_keys = ['structure']
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Missing required config key: {key}")
    
    for field, settings in config['structure'].items():
        if 'path' not in settings:
            raise ValueError(f"Field '{field}' missing JSON path configuration")
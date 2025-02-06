from typing import List, Dict, Any

def key_value_merge(sources: List[Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Merge multiple data sources into a single key-value dictionary
    Args:
        sources: List of data sources to merge
        config: Additional configuration parameters
    Returns:
        Merged dictionary
    """
    merged = {}
    
    for source in sources:
        if isinstance(source, dict):
            merged.update(source)
        elif isinstance(source, list):
            for item in source:
                if isinstance(item, dict):
                    merged.update(item)
                else:
                    merged[str(len(merged))] = item
        else:
            merged[str(len(merged))] = source
    
    return merged

def validate_merge_config(config: Dict[str, Any]):
    """Validate merge function configuration"""
    allowed_keys = ['overwrite', 'key_format']
    for key in config:
        if key not in allowed_keys:
            raise ValueError(f"Invalid config key for key_value_merge: {key}")
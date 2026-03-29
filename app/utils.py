"""
Utility functions for CRM environment.
"""

from typing import Dict, Any, List


def format_entity(entity: Dict[str, Any]) -> str:
    """
    Format entity for display.
    
    Args:
        entity: Entity dict
    
    Returns:
        Formatted string
    """
    return str(entity)


def extract_customer_ids(entities: List[Dict[str, Any]]) -> List[str]:
    """
    Extract customer IDs from entities.
    
    Args:
        entities: List of entity dicts
    
    Returns:
        List of customer IDs
    """
    ids = []
    for entity in entities:
        if "customer_id" in entity:
            ids.append(entity["customer_id"])
    return list(set(ids))


def extract_field_values(entities: List[Dict[str, Any]], field: str) -> List[Any]:
    """
    Extract field values from entities.
    
    Args:
        entities: List of entity dicts
        field: Field name
    
    Returns:
        List of values
    """
    values = []
    for entity in entities:
        if field in entity:
            values.append(entity[field])
    return list(set(values))


def validate_action_schema(action: Dict[str, Any]) -> bool:
    """
    Validate action schema.
    
    Args:
        action: Action dict
    
    Returns:
        True if valid
    """
    if "tool" not in action or "arguments" not in action:
        return False
    if not isinstance(action["tool"], str):
        return False
    if not isinstance(action["arguments"], dict):
        return False
    return True

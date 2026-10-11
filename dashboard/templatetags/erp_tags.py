"""
Custom template tags and filters for TechImport ERP.
"""
import json
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='split')
def split_filter(value, arg=','):
    """
    Split a string by delimiter and trim each item.
    Usage: {{ "item1,item2,item3"|split:"," }}
    """
    if not value:
        return []
    if not isinstance(value, str):
        value = str(value)
    return [item.strip() for item in value.split(arg) if item.strip()]

@register.filter(name='to_json')
def to_json(value):
    """
    Safely serialize python object to JSON string for JS embedding.
    """
    try:
        return mark_safe(json.dumps(value))
    except Exception:
        return '{}'

@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get item from dict safely."""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

"""Serialize dataclasses, or lists of dataclasses, into JSON"""

from dataclasses import is_dataclass, asdict

from .typedefs import JsonType


def serialize(obj: object) -> JsonType:
    """Serialize the item"""
    if is_dataclass(obj):
        return {key: serialize(value) for key, value in asdict(obj).items()}
    if isinstance(obj, list):
        return [serialize(item) for item in obj]
    return obj

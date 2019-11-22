"""Serialize typed structures into less-typed Python objects"""

from dataclasses import is_dataclass, asdict

from .typedefs import JsonType, NamedTupleType


def serialize(obj: object) -> JsonType:
    """Serialize the object into a less-typed form

    Serialize from -> to:
        * Dataclasses -> Dicts
        * NamedTuples -> Dicts
        * Lists -> Lists
        * Dicts -> Dicts
        * Other -> self
    """
    if is_dataclass(obj):
        return {key: serialize(value) for key, value in asdict(obj).items()}
    if isinstance(obj, NamedTupleType):
        return {key: serialize(value) for key, value in obj._asdict().items()}
    if isinstance(obj, dict):
        return {serialize(key): serialize(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [serialize(item) for item in obj]
    return obj

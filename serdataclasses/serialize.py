"""Serialize typed structures into less-typed Python objects"""

from dataclasses import asdict, is_dataclass

from .typedefs import NamedTupleType


def dump(obj: object) -> object:
    """Serialize the object into a less-typed form

    Serialize from -> to:
        * Dataclasses -> Dicts
        * NamedTuples -> Dicts
        * Lists -> Lists
        * Dicts -> Dicts
        * Other -> self
    """
    if is_dataclass(obj):
        return {key: dump(value) for key, value in asdict(obj).items()}
    if isinstance(obj, NamedTupleType):
        return {key: dump(value) for key, value in obj._asdict().items()}
    if isinstance(obj, dict):
        return {dump(key): dump(value) for key, value in obj.items()}
    if isinstance(obj, list):
        return [dump(item) for item in obj]
    return obj

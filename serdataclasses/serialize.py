"""Serialize typed structures into less-typed Python objects."""

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping, Sequence

from .typedefs import NamedTupleType
from .undefined import UNDEFINED


def dump(obj: Any) -> Any:
    """Serialize the object into a less-typed form.

    Serialize from -> to:
        * dataclass -> Dict
        * NamedTuple -> Dict
        * str -> str
        * Sequence -> List
        * Mapping -> Dicts
        * Anything else -> itself
    """
    if is_dataclass(obj):
        return {
            key: dump(value)
            for key, value in asdict(obj).items()
            if value is not UNDEFINED
        }
    if isinstance(obj, NamedTupleType):
        return {
            key: dump(value)
            for key, value in obj._asdict().items()
            if value is not UNDEFINED
        }
    if isinstance(obj, str):
        return obj
    if isinstance(obj, Sequence):
        return [dump(item) for item in obj if item is not UNDEFINED]
    if isinstance(obj, Mapping):
        return {
            dump(key): dump(value)
            for key, value in obj.items()
            if value is not UNDEFINED
        }
    return obj

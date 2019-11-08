"""Deserialize a Python List or Dictionary into a dataclass"""

from dataclasses import is_dataclass, InitVar
from inspect import signature
from typing import Type, Any, Union

from .typedefs import JsonType, T


class DeserializeError(Exception):
    """Exception for when deserialization fails"""


def deserialize(obj: JsonType, constructor: Type[T]) -> T:
    """Deserialize the type"""
    if _is_dataclass(obj, constructor):
        return constructor(
            **{
                p.name: deserialize(obj.get(p.name), p.annotation)
                for p in signature(constructor).parameters.values()
            }
        )
    if _is_list(obj, constructor):
        return [
            deserialize(value, getattr(constructor, "__args__", (object,))[0])
            for value in obj
        ]
    if isinstance(constructor, InitVar):
        return deserialize(obj, constructor.type)
    if (
        _is_nonetype(obj, constructor)
        or _is_any(obj, constructor)
        or _is_primitive(obj, constructor)
    ):
        return obj
    if _is_union(obj, constructor):
        for argument in constructor.__args__:
            try:
                return deserialize(obj, argument)
            except DeserializeError:
                continue
        raise DeserializeError(f"Failed to deserialize {constructor}")

    raise DeserializeError(f"Cannot deserialize {obj} with {constructor}")


def _is_dataclass(obj: JsonType, constructor: Type) -> bool:
    """Check if the type is a dataclasses"""
    if is_dataclass(constructor):
        if not isinstance(obj, dict):
            raise DeserializeError(
                f"{obj} expected to be dict, is actually {type(obj)}"
            )
        return True
    return False


def _is_list(obj: JsonType, constructor: Type) -> bool:
    """Check if the type is a list"""
    if constructor == list or getattr(constructor, "__origin__", None) == list:
        if not isinstance(obj, list):
            raise DeserializeError("Expected a list")
        return True
    return False


def _is_nonetype(obj: JsonType, constructor: Type) -> bool:
    """Check if type is NoneType, or None"""
    if constructor is None or constructor == type(None):
        if not obj is None:
            raise DeserializeError("Expected None")
        return True
    return False


def _is_any(
    obj: JsonType, constructor: Type  # pylint: disable=unused-argument
) -> bool:
    """Check if type is Any"""
    return constructor in (Any, object, InitVar)


def _is_primitive(obj: JsonType, constructor: Type) -> bool:
    """Check if a type is a primitive type"""
    if constructor in (str, int, float, bool):
        if not isinstance(obj, constructor):
            raise DeserializeError(f"Expected {constructor}")
        return True
    return False


def _is_union(
    obj: JsonType, constructor: Type  # pylint: disable=unused-argument
) -> bool:
    """check whether a type is Union

    Note: Optional[str] is an alias for Union[str, NoneType]
    """
    return getattr(constructor, "__origin__", None) == Union

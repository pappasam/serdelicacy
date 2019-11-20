"""Deserialize a Python List or Dictionary into a dataclass"""

import typing
from dataclasses import is_dataclass, InitVar
from typing import get_type_hints, get_args, get_origin
from typing import Type, Any, Union, List, TypeVar

from .typedefs import JsonValuesType, NamedTupleType, T


class DeserializeError(Exception):
    """Exception for deserialization failure

    Deserializing arbitrarily-nested JSON often results in opaque
    deserialization errors. This Exception class provides a clear, consistent
    debugging message. Example:

        serdataclasses.deserialize.DeserializeError: Expected '<class 'int'>'
        but received '<class 'str'>' for value '2'.

        Error location: <class 'test_all.MyDataClass'> >>>
        typing.List[test_all.Another] >>> <class 'test_all.Another'> >>>
        typing.List[int] >>> <class 'int'>
    """

    def __init__(
        self,
        type_expected: Type,
        value_received: object,
        depth: List[Type],
        message_prefix: str = "",
        message_postfix: str = "",
    ):
        message = (
            message_prefix
            + f"Expected '{type_expected}' "
            + f"but received '{type(value_received)}'"
            + f" for value '{value_received}'."
            + message_postfix
        )
        depth_str = " >>> ".join([str(item) for item in depth])
        super().__init__(f"{message}\nError location: {depth_str}")


def deserialize(obj: JsonValuesType, constructor: Type[T]) -> T:
    """Deserialize an object into its constructor

    :param obj: the 'serialized' object that we want to deserialize
    :param constructor: the type into which we want serialize 'obj'
    """
    return _deserialize(obj, constructor, [])


def _deserialize(
    obj: JsonValuesType, constructor: Type[T], depth: List[Type]
) -> T:
    """Deserialize the type

    :param depth: keeps track of recursive position. Supremely helpful for
    error messages, since it shows the user exactly where the parsing fails.

    NOTE: we use typing.get_type_hints because it correctly handles
    ForwardRefs, translating string references into their correct type in
    strange and mysterious ways.
    """
    new_depth = depth + [constructor]
    if _is_dataclass(constructor) or _is_namedtuple(constructor):
        if not isinstance(obj, dict):
            raise DeserializeError(dict, obj, depth)
        return constructor(
            **{
                name: _deserialize(obj.get(name), _type, new_depth)
                for name, _type in get_type_hints(constructor).items()
            }
        )
    if _is_list(constructor):
        if not isinstance(obj, list):
            raise DeserializeError(list, obj, depth)
        return [
            _deserialize(value, get_args(constructor)[0], new_depth)
            for value in obj
        ]
    if _is_initvar(constructor):
        return _deserialize(obj, constructor.type, new_depth)
    if _is_nonetype(constructor):
        if not obj is None:
            raise DeserializeError(type(None), obj, depth)
        return obj
    if _is_primitive(constructor):
        if not isinstance(obj, constructor):
            raise DeserializeError(constructor, obj, depth)
        return obj
    if _is_any(constructor):
        return obj
    if _is_union(constructor):
        _union_errors = []
        for argument in get_args(constructor):
            try:
                return _deserialize(obj, argument, new_depth)
            except DeserializeError as error:
                _union_errors.append(str(error))
        raise DeserializeError(constructor, obj, new_depth)
    if _is_typevar(constructor):
        return _deserialize(
            obj,
            (
                Union[constructor.__constraints__]
                if constructor.__constraints__
                else object
            ),
            new_depth,
        )

    raise DeserializeError(
        constructor, obj, new_depth, message_prefix="Unsupported type. "
    )


def _is_dataclass(constructor: Type) -> bool:
    """Check if the type is a dataclasses"""
    return is_dataclass(constructor)


def _is_initvar(constructor: Type) -> bool:
    """Check if the type is an InitVar"""
    return isinstance(constructor, InitVar)


def _is_list(constructor: Type) -> bool:
    """Check if the type is a list"""
    return constructor == list or get_origin(constructor) == list


def _is_nonetype(constructor: Type) -> bool:
    """Check if type is NoneType, or None"""
    return constructor == type(None)


def _is_any(constructor: Type) -> bool:
    """Check if type is Any"""
    return constructor in (Any, object, InitVar)


def _is_primitive(constructor: Type) -> bool:
    """Check if a type is a primitive type"""
    return constructor in (str, int, float, bool)


def _is_union(constructor: Type) -> bool:
    """check whether a type is Union

    Note: Optional[str] is an alias for Union[str, NoneType]
    """
    return get_origin(constructor) == Union


def _is_typevar(constructor: Type) -> bool:
    """Check if a type is a TypeVar"""
    return isinstance(constructor, TypeVar)


def _is_namedtuple(constructor: Type) -> bool:
    """Check if a type is a NamedTuple"""
    return isinstance(constructor, NamedTupleType)

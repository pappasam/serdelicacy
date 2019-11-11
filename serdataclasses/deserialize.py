"""Deserialize a Python List or Dictionary into a dataclass"""

from dataclasses import is_dataclass, InitVar
from typing import get_type_hints
from typing import Type, Any, Union, List

from .typedefs import JsonValuesType, T


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
        self, type_expected: Type, value_received: object, depth: List[Type]
    ):
        message = (
            f"Expected '{type_expected}' but received '{type(value_received)}'"
            f" for value '{value_received}'."
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
    if _is_dataclass(obj, constructor, new_depth):
        return constructor(
            **{
                name: _deserialize(obj.get(name), _type, new_depth)
                for name, _type in get_type_hints(constructor).items()
            }
        )
    if _is_list(obj, constructor, new_depth):
        return [
            _deserialize(
                value,
                getattr(constructor, "__args__", (object,))[0],
                new_depth,
            )
            for value in obj
        ]
    if isinstance(constructor, InitVar):
        return _deserialize(obj, constructor.type, new_depth)
    if (
        _is_nonetype(obj, constructor, new_depth)
        or _is_any(obj, constructor, new_depth)
        or _is_primitive(obj, constructor, new_depth)
    ):
        return obj
    if _is_union(obj, constructor, new_depth):
        _union_errors = []
        for argument in constructor.__args__:
            try:
                return _deserialize(obj, argument, new_depth)
            except DeserializeError as error:
                _union_errors.append(str(error))
        raise DeserializeError(constructor, obj, new_depth)

    raise DeserializeError(constructor, obj, new_depth)


def _is_dataclass(
    obj: JsonValuesType, constructor: Type, depth: List[Type]
) -> bool:
    """Check if the type is a dataclasses"""
    if is_dataclass(constructor):
        if not isinstance(obj, dict):
            raise DeserializeError(dict, obj, depth)
        return True
    return False


def _is_list(
    obj: JsonValuesType, constructor: Type, depth: List[Type]
) -> bool:
    """Check if the type is a list"""
    if constructor == list or getattr(constructor, "__origin__", None) == list:
        if not isinstance(obj, list):
            raise DeserializeError(list, obj, depth)
        return True
    return False


def _is_nonetype(
    obj: JsonValuesType, constructor: Type, depth: List[Type]
) -> bool:
    """Check if type is NoneType, or None"""
    if constructor == type(None):
        if not obj is None:
            raise DeserializeError(type(None), obj, depth)
        return True
    return False


def _is_any(
    obj: JsonValuesType,  # pylint: disable=unused-argument
    constructor: Type,
    depth: List[Type],  # pylint: disable=unused-argument
) -> bool:
    """Check if type is Any"""
    return constructor in (Any, object, InitVar)


def _is_primitive(
    obj: JsonValuesType, constructor: Type, depth: List[Type]
) -> bool:
    """Check if a type is a primitive type"""
    if constructor in (str, int, float, bool):
        if not isinstance(obj, constructor):
            raise DeserializeError(constructor, obj, depth)
        return True
    return False


def _is_union(
    obj: JsonValuesType,  # pylint: disable=unused-argument
    constructor: Type,
    depth: List[Type],  # pylint: disable=unused-argument
) -> bool:
    """check whether a type is Union

    Note: Optional[str] is an alias for Union[str, NoneType]
    """
    return getattr(constructor, "__origin__", None) == Union

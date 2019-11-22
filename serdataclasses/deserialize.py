"""Deserialize a Python List or Dictionary into a dataclass, list, or other
supported structure"""

import itertools
from dataclasses import InitVar, dataclass, field, is_dataclass
from typing import get_args  # type: ignore
from typing import get_origin  # type: ignore
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    List,
    Type,
    TypeVar,
    Union,
    get_type_hints,
)

from .typedefs import NamedTupleType, NoResult, Possible, T, is_no_result


def load(obj: object, constructor: Type[T]) -> T:
    """Deserialize an object into its constructor

    :param obj: the 'serialized' object that we want to deserialize
    :param constructor: the type into which we want serialize 'obj'
    """
    return Deserialize(obj, constructor, []).run()


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


@dataclass
class Deserialize(Generic[T]):
    """Deserialize the type

    :param depth: keeps track of recursive position. Supremely helpful for
    error messages, since it shows the user exactly where the parsing fails.

    NOTE: we use typing.get_type_hints because it correctly handles
    ForwardRefs, translating string references into their correct type in
    strange and mysterious ways.
    """

    obj: object
    constructor: Type[T]
    depth: List[Type]
    new_depth: List[Type] = field(init=False)
    check_functions: Iterable[Callable[[], Possible[T]]] = field(init=False)

    def __post_init__(self) -> None:
        """Initialize the uninitialized"""
        self.new_depth = self.depth + [self.constructor]
        self.check_functions = (
            self._check_mapping_class,
            self._check_list,
            self._check_dict,
            self._check_initvar,
            self._check_none,
            self._check_primitive,
            self._check_any,
            self._check_union,
            self._check_typevar,
            self._final_error,
        )

    def run(self) -> T:
        """Run each function in the iterator"""
        return next(
            itertools.dropwhile(
                is_no_result, (function() for function in self.check_functions)
            )
        )  # type: ignore

    def _check_mapping_class(self) -> Possible[T]:
        """Checks whether a result is a mapping type"""
        if _is_dataclass(self.constructor) or _is_namedtuple(self.constructor):
            if not isinstance(self.obj, dict):
                raise DeserializeError(dict, self.obj, self.new_depth)
            return self.constructor(
                **{
                    name: Deserialize(
                        self.obj.get(name), _type, self.new_depth
                    ).run()
                    for name, _type in get_type_hints(self.constructor).items()
                }
            )  # type: ignore
        return NoResult

    def _check_list(self) -> Possible[T]:
        """Checks whether a result is a list type"""
        if _is_list(self.constructor):
            if not isinstance(self.obj, list):
                raise DeserializeError(list, self.obj, self.new_depth)
            _nc = get_args(self.constructor)
            _args = _nc[0] if _nc else Any
            return [
                Deserialize(value, _args, self.new_depth).run()
                for value in self.obj
            ]  # type: ignore
        return NoResult

    def _check_dict(self) -> Possible[T]:
        """Checks whether a result is a dict type"""
        if _is_dict(self.constructor):
            if not isinstance(self.obj, dict):
                raise DeserializeError(dict, self.obj, self.new_depth)
            _nc = get_args(self.constructor)
            _tpkey, _tpvalue = _nc if _nc else (Any, Any)
            # fmt: off
            return {
                Deserialize(key, _tpkey, self.new_depth).run(): Deserialize(
                    value,
                    _tpvalue,
                    self.new_depth,
                ).run()
                for key, value in self.obj.items()
            }  # type: ignore
            # fmt: on
        return NoResult

    def _check_initvar(self) -> Possible[T]:
        """Checks if a result is an InitVar"""
        if _is_initvar(self.constructor):
            return Deserialize(
                self.obj,
                self.constructor.type,  # type: ignore
                self.new_depth,
            ).run()
        return NoResult

    def _check_none(self) -> Possible[T]:
        """Checks if a result is None"""
        if _is_nonetype(self.constructor):
            if not self.obj is None:
                raise DeserializeError(type(None), self.obj, self.new_depth)
            return self.obj  # type: ignore
        return NoResult

    def _check_primitive(self) -> Possible[T]:
        """Check if result is a primitive"""
        if _is_primitive(self.constructor):
            if not isinstance(self.obj, self.constructor):
                raise DeserializeError(
                    self.constructor, self.obj, self.new_depth
                )
            return self.obj
        return NoResult

    def _check_any(self) -> Possible[T]:
        """Check if result is Any"""
        if _is_any(self.constructor):
            return self.obj  # type: ignore
        return NoResult

    def _check_union(self) -> Possible[T]:
        """Check if result is a Union"""
        if _is_union(self.constructor):
            for argument in get_args(self.constructor):
                try:
                    return Deserialize(
                        self.obj, argument, self.new_depth
                    ).run()
                except DeserializeError:
                    pass
            raise DeserializeError(self.constructor, self.obj, self.new_depth)
        return NoResult

    def _check_typevar(self) -> Possible[T]:
        """Checks whether it's a typevar"""
        if _is_typevar(self.constructor):
            return Deserialize(
                self.obj,
                (
                    Union[self.constructor.__constraints__]  # type: ignore
                    if self.constructor.__constraints__  # type: ignore
                    else object
                ),
                self.new_depth,
            ).run()
        return NoResult

    def _final_error(self) -> Possible[T]:
        """Finally, if nothing is caught, raise an exception

        Implemented like this so it can be the last argument. All it actually
        does is raise a DeserializeError.
        """
        raise DeserializeError(
            self.constructor,
            self.obj,
            self.new_depth,
            message_prefix="Unsupported type. ",
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


def _is_dict(constructor: Type) -> bool:
    """Check if the type is a dict"""
    return constructor == dict or get_origin(constructor) == dict


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
    return isinstance(constructor, TypeVar)  # type: ignore


def _is_namedtuple(constructor: Type) -> bool:
    """Check if a type is a NamedTuple"""
    return isinstance(constructor, NamedTupleType)

"""Recursively deserialize a Python Sequence, Mapping, or primitive into a.

* dataclass
* NamedTuple
* list
* tuple
* other supported structure
"""

import inspect
import itertools
from dataclasses import InitVar, dataclass, field, is_dataclass
from typing import _TypedDictMeta  # type: ignore
from typing import (
    Any,
    Callable,
    Generic,
    Iterable,
    List,
    Mapping,
    Sequence,
    Tuple,
    Type,
    TypeVar,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from .errors import DepthContainer, DeserializeError
from .typedefs import (
    NO_RESULT,
    UNDEFINED,
    NamedTupleType,
    PossibleResult,
    Undefined,
)

T = TypeVar("T")  # pylint: disable=invalid-name


def _is_no_result(obj: Any) -> bool:
    """Helper function to determine whether a value is NO_RESULT."""
    return obj is NO_RESULT


def load(
    obj: Any,
    constructor: Type[T],
    typesafe_constructor: bool = True,
    convert_primitives: bool = True,
) -> T:
    """Deserialize an object into its constructor.

    :param obj: the 'serialized' object that we want to deserialize
    :param constructor: the type into which we want serialize 'obj'
    :param typesafe_constructor: makes sure that the provided top-level
        constructor is not one of several "unsafe" types
    :param convert_primitives: automatically convert primitive values, if
        encountered. Even if enabled here, this becomes automatically disabled,
        recursively downward, if an ambiguous container type is encountered. At
        this time, `Union` is considered ambiguous. Note: according to the type
        system, `Optional` is considered a `Union` type, but this special case
        does not disable automatic conversion (special-cased code handles).

    :returns: an instance of your constructor, recursively filled

    :raises TypeError: if typesafe is True and a non-typesafe constructor is
        provided
    :raises errors.DeserializeError: triggered by any deserialization error
    """
    if typesafe_constructor and any(
        check(constructor) for check in _TYPE_UNSAFE_CHECKS
    ):
        raise TypeError(f"Cannot begin deserialization with '{constructor}'")
    return Deserialize(
        obj=obj,
        constructor=constructor,
        depth=[],
        convert_primitives=convert_primitives,
    ).run()


@dataclass
class Deserialize(Generic[T]):  # pylint: disable=too-many-instance-attributes
    """Deserialize the type.

    :attr depth: keeps track of recursive position. Supremely helpful for
        error messages, since it shows the user exactly where the parsing
        fails.

    NOTE: we use typing.get_type_hints because it correctly handles
    ForwardRefs, translating string references into their correct type in
    strange and mysterious ways.
    """

    obj: Any
    constructor: Type[T]
    depth: InitVar[List[DepthContainer]]
    convert_primitives: bool
    key: Any = UNDEFINED
    new_depth: List[DepthContainer] = field(init=False)
    constructor_args: Tuple[Type, ...] = field(init=False)
    constructor_origin: Type = field(init=False)
    check_functions: Iterable[Callable[[], PossibleResult[T]]] = field(
        init=False
    )

    def __post_init__(self, depth) -> None:
        """Initialize the uninitialized."""
        self.new_depth = depth + [DepthContainer(self.constructor, self.obj)]
        self.constructor_args = get_args(self.constructor)
        origin = get_origin(self.constructor)
        self.constructor_origin = origin if origin else self.constructor
        self.check_functions = (
            self._check_any,
            self._check_primitive,
            self._check_none,
            self._check_undefined,
            self._check_dataclass,
            self._check_namedtuple,
            self._check_typed_dict,
            self._check_tuple,
            self._check_sequence,
            self._check_mapping,
            self._check_initvar_instance,
            self._check_union,
            self._check_typevar,
        )

    def run(self) -> T:
        """Run each function in the iterator."""
        try:
            return next(
                itertools.dropwhile(
                    _is_no_result,
                    (function() for function in self.check_functions),
                )
            )  # type: ignore
        except StopIteration:
            # pylint: disable=raise-missing-from
            raise DeserializeError(
                self.constructor,
                self.obj,
                self.new_depth,
                self.key,
                message_prefix="Unsupported type. ",
            )
        except Exception as error:
            if not isinstance(error, DeserializeError):
                raise DeserializeError(
                    self.constructor,
                    self.obj,
                    self.new_depth,
                    self.key,
                    message_override=str(error),
                ) from error
            raise

    def _check_dataclass(self) -> PossibleResult[T]:
        """Checks whether a result is a dataclass."""
        if is_dataclass(self.constructor):
            if not isinstance(self.obj, Mapping):
                raise DeserializeError(
                    Mapping, self.obj, self.new_depth, self.key
                )
            parameters = inspect.signature(self.constructor).parameters
            return self.constructor(
                **{
                    name: Deserialize(
                        obj=self.obj.get(name, UNDEFINED),
                        constructor=_type,
                        depth=self.new_depth,
                        convert_primitives=self.convert_primitives,
                        key=name,
                    ).run()
                    for name, _type in get_type_hints(self.constructor).items()
                    if not (
                        name not in self.obj
                        and name in parameters
                        and parameters[name].default != inspect.Signature.empty
                    )
                }
            )  # type: ignore
        return NO_RESULT

    def _check_namedtuple(self) -> PossibleResult[T]:
        """Checks whether a result is a namedtuple."""
        if isinstance(self.constructor, NamedTupleType):
            if not isinstance(self.obj, Mapping):
                raise DeserializeError(
                    Mapping, self.obj, self.new_depth, self.key
                )
            parameters = inspect.signature(self.constructor).parameters
            return self.constructor(
                **{
                    name: Deserialize(
                        obj=self.obj.get(name, UNDEFINED),
                        constructor=_type,
                        depth=self.new_depth,
                        convert_primitives=self.convert_primitives,
                        key=name,
                    ).run()
                    for name, _type in get_type_hints(self.constructor).items()
                    if not (
                        name not in self.obj
                        and name in parameters
                        and parameters[name].default != inspect.Signature.empty
                    )
                }
            )  # type: ignore
        return NO_RESULT

    def _check_tuple(self) -> PossibleResult[T]:
        """Checks whether a result is a Tuple type."""
        if isinstance(self.constructor_origin, type) and issubclass(
            self.constructor_origin, tuple
        ):
            if not isinstance(self.obj, Sequence):
                raise DeserializeError(
                    tuple, self.obj, self.new_depth, self.key
                )
            if not self.constructor_args:
                return self.constructor_origin(self.obj)  # type: ignore
            if (
                len(self.constructor_args) == 2
                and self.constructor_args[1] == ...
            ):
                return self.constructor_origin(
                    Deserialize(
                        obj=value,
                        constructor=self.constructor_args[0],
                        depth=self.new_depth,
                        convert_primitives=self.convert_primitives,
                    ).run()
                    for value in self.obj
                )  # type: ignore
            if len(self.constructor_args) != len(self.obj):
                raise DeserializeError(
                    tuple,
                    self.obj,
                    self.new_depth,
                    self.key,
                    message_prefix="Tuple incorrect length. ",
                )
            return self.constructor_origin(
                Deserialize(
                    obj=self.obj[i],
                    constructor=arg,
                    depth=self.new_depth,
                    convert_primitives=self.convert_primitives,
                ).run()
                for i, arg in enumerate(self.constructor_args)
            )  # type: ignore
        return NO_RESULT

    def _check_sequence(self) -> PossibleResult[T]:
        """Checks whether a result is a Sequence type.

        Catches generic sequences. All sequence types that are treated
        differently (such as strings) should be placed before this
        function.
        """
        if isinstance(self.constructor_origin, type) and issubclass(
            self.constructor_origin, Sequence
        ):
            if not isinstance(self.obj, Sequence):
                raise DeserializeError(
                    Sequence, self.obj, self.new_depth, self.key
                )
            if self.constructor_args:
                _arg = self.constructor_args[0]
            else:
                _arg = Any  # type: ignore
            return self.constructor_origin(
                Deserialize(
                    obj=value,
                    constructor=_arg,
                    depth=self.new_depth,
                    convert_primitives=self.convert_primitives,
                ).run()
                for value in self.obj
            )  # type: ignore
        return NO_RESULT

    def _check_mapping(self) -> PossibleResult[T]:
        """Checks whether a result is a Mapping type.

        Catches generic mappings. All mapping types that are treated
        differently should be placed before this function.
        """
        if isinstance(self.constructor_origin, type) and issubclass(
            self.constructor_origin, Mapping
        ):
            if not isinstance(self.obj, Mapping):
                raise DeserializeError(
                    Mapping, self.obj, self.new_depth, self.key
                )
            if self.constructor_args:
                _tpkey = self.constructor_args[0]
                _tpvalue = self.constructor_args[1]
            else:
                _tpkey = Any  # type: ignore
                _tpvalue = Any  # type: ignore
            return self.constructor_origin(
                {
                    Deserialize(
                        obj=key,
                        constructor=_tpkey,
                        depth=self.new_depth,
                        convert_primitives=self.convert_primitives,
                    )
                    .run(): Deserialize(
                        obj=value,
                        constructor=_tpvalue,
                        depth=self.new_depth,
                        convert_primitives=self.convert_primitives,
                        key=key,
                    )
                    .run()
                    for key, value in self.obj.items()
                }
            )  # type: ignore
        return NO_RESULT

    def _check_typed_dict(self) -> PossibleResult[T]:
        """Checks whether a result is a typing.TypedDict."""
        # pylint: disable=unidiomatic-typecheck
        if type(self.constructor) == _TypedDictMeta:
            # pylint: enable=unidiomatic-typecheck
            if not isinstance(self.obj, dict):
                raise DeserializeError(
                    dict, self.obj, self.new_depth, self.key
                )
            return {
                name: Deserialize(
                    obj=self.obj.get(name, UNDEFINED),
                    constructor=_type,
                    depth=self.new_depth,
                    convert_primitives=self.convert_primitives,
                    key=name,
                ).run()
                for name, _type in get_type_hints(self.constructor).items()
            }  # type: ignore
        return NO_RESULT

    def _check_initvar_instance(self) -> PossibleResult[T]:
        """Checks if a result is a dataclasses.InitVar."""
        if _is_initvar_instance(self.constructor):
            return Deserialize(
                obj=self.obj,
                constructor=self.constructor.type,  # type: ignore
                depth=self.new_depth,
                convert_primitives=self.convert_primitives,
            ).run()
        return NO_RESULT

    def _check_none(self) -> PossibleResult[T]:
        """Checks if a result is None."""
        if self.constructor == type(None):
            if not self.obj is None:
                raise DeserializeError(
                    type(None), self.obj, self.new_depth, self.key
                )
            return self.obj  # type: ignore
        return NO_RESULT

    def _check_undefined(self) -> PossibleResult[T]:
        """Checks if a result is UNDEFINED.

        This case is extremely rare / somewhat nonsensical, but is
        included here for completeness sake.
        """
        if self.constructor == Undefined:
            if not self.obj is UNDEFINED:
                raise DeserializeError(
                    Undefined, self.obj, self.new_depth, self.key
                )
            return self.obj  # type: ignore
        return NO_RESULT

    def _check_primitive(self) -> PossibleResult[T]:
        """Check if result is a primitive.

        If `self.convert_primitives` is `True`, tries to automatically
        convert primitive value to the specified type.

        `None` and `UNDEFINED` are both considered "unconvertable"
        """
        if self.constructor in _PRIMITIVES:
            if self.obj is UNDEFINED:
                raise DeserializeError(
                    self.constructor, self.obj, self.new_depth, self.key
                )
            if self.obj is None:
                raise DeserializeError(
                    self.constructor, self.obj, self.new_depth, self.key
                )
            if not isinstance(self.obj, self.constructor):
                if not self.convert_primitives:
                    raise DeserializeError(
                        self.constructor, self.obj, self.new_depth, self.key
                    )
                try:
                    return self.constructor(self.obj)  # type: ignore
                except (ValueError, TypeError) as error:
                    raise DeserializeError(
                        self.constructor, self.obj, self.new_depth, self.key
                    ) from error
            return self.obj
        return NO_RESULT

    def _check_any(self) -> PossibleResult[T]:
        """Check if result is typing.Any."""
        if _is_any(self.constructor):
            return self.obj  # type: ignore
        return NO_RESULT

    def _check_union(self) -> PossibleResult[T]:
        """Check if result is a Union.

        Encountering this type usually recursively disables
        `convert_primitives` for items found within the `Union`. The
        exception are `Optional` types, which are really `Union[Any,
        None]` and common enough for us to find a workaround.
        """
        if _is_union(self.constructor):
            args = get_args(self.constructor)
            is_optional = len(args) == 2 and type(None) in args
            is_optional_property = len(args) == 2 and Undefined in args
            if is_optional and self.obj is None:
                return None  # type: ignore
            if is_optional_property and self.obj is UNDEFINED:
                return UNDEFINED  # type: ignore
            for argument in args:
                convert_primitives = self.convert_primitives and (
                    (is_optional and argument != type(None))
                    or (is_optional_property and argument != Undefined)
                )
                try:
                    return Deserialize(
                        obj=self.obj,
                        constructor=argument,
                        depth=self.new_depth,
                        convert_primitives=convert_primitives,
                    ).run()
                except DeserializeError:
                    pass
            raise DeserializeError(
                self.constructor, self.obj, self.new_depth, self.key
            )
        return NO_RESULT

    def _check_typevar(self) -> PossibleResult[T]:
        """Checks whether it's a typevar."""
        if _is_typevar(self.constructor):  # type: ignore
            return Deserialize(
                obj=self.obj,
                constructor=(
                    Union[self.constructor.__constraints__]  # type: ignore
                    if self.constructor.__constraints__  # type: ignore
                    else object
                ),
                depth=self.new_depth,
                convert_primitives=self.convert_primitives,
            ).run()
        return NO_RESULT


def _is_initvar_instance(typeval: Type) -> bool:
    """Check if a type is an InitVar with a type inside."""
    return isinstance(typeval, InitVar)


def _is_any(typeval: Type) -> bool:
    """Check if a type is the equivalent to Any."""
    return typeval in _ANY


def _is_union(typeval: Type) -> bool:
    """Check if a type is a Union."""
    return get_origin(typeval) is Union


def _is_typevar(typeval: Type) -> bool:
    """Check if a type is a TypeVar."""
    return isinstance(typeval, TypeVar)  # type: ignore


_TYPE_UNSAFE_CHECKS = (
    _is_any,
    _is_initvar_instance,
    _is_typevar,
    _is_union,
)

_PRIMITIVES = {str, int, float, bool}

_ANY = {Any, object, InitVar}

_UNION_PRIMITIVE_ALLOW_CONVERSION = {type(None), Undefined}

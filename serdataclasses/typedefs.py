"""Type definitions."""

import enum
from typing import Protocol, TypeVar, Union, runtime_checkable

# pylint: disable=too-few-public-methods
# pylint: disable=missing-function-docstring

T = TypeVar("T")  # pylint: disable=invalid-name


class Undefined(enum.Enum):
    """Handles JavaScript/TypeScript `undefined` / optional properties.

    TypeScript / JavaScript /  have 2 words that indicate something is missing:

    - `undefined` == an attribute has not been defined
    - `null` == an attribute's value is `null`
    """

    token = 0

    def __repr__(self) -> str:
        return "<Undefined property>"

    def __bool__(self) -> bool:
        return False


OptionalProperty = Union[Undefined, T]

UNDEFINED = Undefined.token


class NoResult(enum.Enum):
    """Special case type to indicate that a function returns no result.

    Useful because `None`, which most functions return implicitly, is
    `null` in JSON and therefore important for serde.
    """

    token = 0

    def __bool__(self) -> bool:
        return False


PossibleResult = Union[NoResult, T]

NO_RESULT = NoResult.token


@runtime_checkable
class NamedTupleType(Protocol):
    """NamedTuple protocol; methods only associated with namedtuples."""

    def _make(self):
        ...

    def _asdict(self):
        ...

    def _replace(self):
        ...

    def _fields(self):
        ...

    def _field_defaults(self):
        ...

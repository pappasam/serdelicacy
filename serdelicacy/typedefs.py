"""Type definitions."""

import enum
from typing import Any, Protocol, TypeVar, Union, runtime_checkable

# pylint: disable=too-few-public-methods
# pylint: disable=missing-function-docstring

T = TypeVar("T")  # pylint: disable=invalid-name


class Missing(enum.Enum):
    """Handles missing JSON values.

    TypeScript / JavaScript /  have 2 words that indicate something is
    conceptually missing:

    - `undefined` == an attribute has not been defined. This concept is
        represented by this class
    - `null` == an attribute's value is `null`. This concept is represented by
        the Python value `None`.
    """

    token = 0

    def __repr__(self) -> str:
        return "<Missing property>"

    def __bool__(self) -> bool:
        return False


OptionalProperty = Union[Missing, T]
OptionalProperty.__doc__ = """Type alias for a value that can be MISSING

`OptionalProperty` is extremely useful when differentiating between values that
can be missing and those that are `None`.
"""


MISSING = Missing.token


def is_missing(value: Any) -> bool:
    """Check whether `value` is `MISSING`

    Prevents users from needing to import `MISSING` constant.

    Parameters:
        value: any Python object

    Returns:
        `True` if a value is `MISSING`, `False` otherwise
    """
    return value is MISSING


def get(value: Union[Missing, T], default: T) -> T:
    """Return `value` unless it's `MISSING`, in which case return `default`.

    Similar to `dict.get`, but operates on `OptionalProperty`, provides no
    default for `default`, and is typesafe.

    Parameters:
        value: an `OptionalProperty`
        default: a value of the same type as `value`'s inner non-`MISSING` type

    Returns:
        `default` if `value` is `MISSING`, otherwise `value`
    """
    return default if value is MISSING else value  # type: ignore


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

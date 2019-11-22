"""Type definitions

A JSON type that would be nice if recursive types were supported:

    JsonValuesType = Union[
        str,
        int,
        float,
        bool,
        None,
        Dict[str, "JsonValuesType"],
        List["JsonValuesType"],
    ]

    JsonType = Union[Dict[str, JsonValuesType], List[JsonValuesType]]
"""

from typing import Protocol, Type, TypeVar, Union, final, runtime_checkable

# pylint: disable=too-few-public-methods
# pylint: disable=missing-function-docstring


@final
class NoResult:
    """This value represents no result. Necessary because we care about None"""

    def __new__(cls) -> Type["NoResult"]:  # type: ignore
        """Simply returns reference to itself, making a defacto singleton"""
        return cls


_V = TypeVar("_V")

Possible = Union[_V, Type[NoResult]]  # pylint: disable=invalid-name

T = TypeVar("T")  # pylint: disable=invalid-name


def is_no_result(value: object) -> bool:
    """Checks if value is NoResult"""
    return value is NoResult


@runtime_checkable
class NamedTupleType(Protocol):
    """NamedTuple protocol; methods only associated with namedtuples"""

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

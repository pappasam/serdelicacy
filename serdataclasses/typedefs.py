"""Type definitions"""

from typing import (
    Dict,
    List,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)


class NoResult:
    """This value represents no result. Necessary because we care about None"""

    def __call__(self):
        """Simply returns reference to itself, making a defacto singleton"""
        return self


_V = TypeVar("_V")

Possible = Union[_V, NoResult]  # pylint: disable=invalid-name

T = TypeVar("T")  # pylint: disable=invalid-name


def is_no_result(value: object) -> bool:
    """Checks if value is NoResult"""
    return value is NoResult


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

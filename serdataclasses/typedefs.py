"""Type definitions"""

from typing import (
    Dict,
    List,
    Protocol,
    TypeVar,
    Union,
    runtime_checkable,
)


T = TypeVar("T")  # pylint: disable=invalid-name

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

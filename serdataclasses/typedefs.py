"""Type definitions"""

from typing import Union, Dict, List, TypeVar


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

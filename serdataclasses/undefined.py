"""Handles JavaScript/TypeScript `undefined` / optional properties.

TypeScript / JavaScript /  have 2 words that indicate something is missing:

- `undefined` == an attribute has not been defined
- `null` == an attribute's value is `null`
"""


import enum
from typing import TypeVar, Union

T = TypeVar("T")  # pylint: disable=invalid-name


class Undefined(enum.Enum):
    """Equivalent to Javascript's undefined."""

    token = 0

    def __repr__(self) -> str:
        return "<Undefined property>"


OptionalProperty = Union[Undefined, T]

UNDEFINED = Undefined.token

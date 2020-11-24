"""Custom Exceptions for serdelicacy."""

import json
from typing import Any, List, NamedTuple, Type

from .typedefs import MISSING


class DepthContainer(NamedTuple):
    """Contain information."""

    constructor: Type
    key: Any
    value: Any


class SerdeError(Exception):
    """Root error for serdelicacy."""


def _tc_enc(value: str, code: int = 32) -> str:
    """Encode error message values with terminal colors.

    See:
        - <https://i.stack.imgur.com/9UVnC.png>
        - <https://stackoverflow.com/a/61273717>

    For Python's somewhat-poorly-documented encodings:
        <https://docs.python.org/3/library/codecs.html#text-encodings>

    Some color options:
        - 30: black
        - 31: red
        - 32: green
        - 33: yellow
        - 34: blue
        - 35: magenta
        - 36: cyan
        - 37: white
    """
    return f"\u001b[{code}m{value}\u001b[0m"


_K_KEY = _tc_enc("key", 32)
_K_VALUE = _tc_enc("value", 32)
_K_TYPE = _tc_enc("type", 34)
_K_INPUT = _tc_enc("input", 34)
_K_ERROR = _tc_enc("error", 31)


class DeserializeError(SerdeError):
    """Deserialization failure.

    Deserializing arbitrarily-nested JSON often results in opaque
    deserialization errors. This Exception class provides a clear,
    consistent debugging message.
    """

    # pylint: disable=too-many-arguments

    def __init__(
        self,
        type_expected: Type,
        value_received: Any,
        depth: List[DepthContainer],
        key: Any,
        message_prefix: str = "",
        message_postfix: str = "",
        message_override: str = "",
    ):
        depth_messages = []
        for depth_item in depth:
            value = {
                _K_KEY: repr(depth_item.key),
                _K_VALUE: {
                    _K_TYPE: repr(depth_item.constructor),
                    _K_INPUT: repr(depth_item.value),
                },
            }
            if depth_item.key is MISSING:
                del value[_K_KEY]
            depth_messages.append(value)

        if message_override:
            message = message_override
        elif value_received is MISSING and key is not MISSING:
            message = f"missing required key {repr(key)}"
            depth_messages.pop()
        else:
            message = (
                message_prefix
                + f"expected {repr(type_expected)} "
                + f"but received {repr(type(value_received))} "
                + message_postfix
            )
        depth_messages[-1][_K_ERROR] = message.strip()
        depth_str = json.dumps(depth_messages, indent=2)
        super().__init__(
            f"{message}\n{depth_str}".encode().decode("unicode-escape")
        )

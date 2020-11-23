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
                "key": repr(depth_item.key),
                "value": {
                    "type_expected": repr(depth_item.constructor),
                    "object_received": repr(depth_item.value),
                },
            }
            if depth_item.key is MISSING:
                del value["key"]
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
        depth_messages[-1]["error"] = message
        depth_str = json.dumps(depth_messages, indent=2)
        super().__init__(f"{message}\n{depth_str}")

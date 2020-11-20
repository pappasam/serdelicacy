"""Custom Exceptions for serdataclasses."""

from typing import Any, List, NamedTuple, Type

from .typedefs import UNDEFINED


class DepthContainer(NamedTuple):
    """Contain information."""

    constructor: Type
    value: Any


class SerdeError(Exception):
    """Root error for serdataclasses."""


class DeserializeError(SerdeError):
    """Deserialization failure.

    Deserializing arbitrarily-nested JSON often results in opaque
    deserialization errors. This Exception class provides a clear, consistent
    debugging message. Example:

        serdataclasses.deserialize.DeserializeError: Expected '<class 'int'>'
        but received '<class 'str'>' for value '2'.

        Error location: <class 'test_all.MyDataClass'> >>>
        typing.List[test_all.Another] >>> <class 'test_all.Another'> >>>
        typing.List[int] >>> <class 'int'>
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
        depth_messages = [
            {repr(depth_item.constructor): repr(depth_item.value)}
            for depth_item in depth
        ]
        if message_override:
            message = message_override
        elif value_received is UNDEFINED and key is not UNDEFINED:
            message = f"missing required key {repr(key)}"
            depth_messages.pop()
        else:
            message = (
                message_prefix
                + f"expected {repr(type_expected)} "
                + f"but received {repr(type(value_received))} "
                + message_postfix
            )
        len_depth = len(depth_messages)
        depth_str = "  " + "\n  ".join(
            (
                f"{len_depth - i}. {repr(depth_message).strip('{} ')}"
                for i, depth_message in enumerate(reversed(depth_messages))
            )
        )
        super().__init__(f"{message}\n{depth_str}")

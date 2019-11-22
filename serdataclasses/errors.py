"""Custom Exceptions for serdataclasses"""

from typing import List, Type


class DeserializeError(Exception):
    """Exception for deserialization failure

    Deserializing arbitrarily-nested JSON often results in opaque
    deserialization errors. This Exception class provides a clear, consistent
    debugging message. Example:

        serdataclasses.deserialize.DeserializeError: Expected '<class 'int'>'
        but received '<class 'str'>' for value '2'.

        Error location: <class 'test_all.MyDataClass'> >>>
        typing.List[test_all.Another] >>> <class 'test_all.Another'> >>>
        typing.List[int] >>> <class 'int'>
    """

    def __init__(
        self,
        type_expected: Type,
        value_received: object,
        depth: List[Type],
        message_prefix: str = "",
        message_postfix: str = "",
    ):
        message = (
            message_prefix
            + f"Expected '{type_expected}' "
            + f"but received '{type(value_received)}'"
            + f" for value '{value_received}'."
            + message_postfix
        )
        depth_str = " >>> ".join([str(item) for item in depth])
        super().__init__(f"{message}\nError location: {depth_str}")

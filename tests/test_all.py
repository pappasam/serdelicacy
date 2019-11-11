"""Test the deserialize class"""

from dataclasses import dataclass
from typing import List, Union, Optional

from serdataclasses.deserialize import deserialize
from serdataclasses.serialize import serialize


@dataclass
class Another:
    y: List[int]


@dataclass
class MyDataClass:
    x: int
    y: str
    z: float
    l: List["Another"]
    q: Optional[str]
    p: List[Union[Another, str]]


value = {
    "x": 12,
    "y": "hello",
    "z": 12.41,
    "l": [{"y": [1, 2, 3]}, {"y": [4, 5, 6]}],
    "p": ["hello", "world", {"y": [1, 2, 3]}, {"y": [4, 5, 6]}],
}

deserialized = deserialize(value, MyDataClass)

serialized = serialize(deserialized)

expected_deserialized = MyDataClass(
    x=12,
    y="hello",
    z=12.41,
    l=[Another(y=[1, 2, 3]), Another(y=[4, 5, 6])],
    q=None,
    p=["hello", "world", Another(y=[1, 2, 3]), Another(y=[4, 5, 6])],
)

expected_serialized = {
    **value,
    "q": None,
}


def test_deserialize():
    assert deserialized == expected_deserialized


def test_serialize():
    assert serialized == expected_serialized

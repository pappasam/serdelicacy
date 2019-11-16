"""Test the deserialize class"""

from dataclasses import dataclass
from typing import List, Union, Optional

from serdataclasses.deserialize import deserialize
from serdataclasses.serialize import serialize

from hypothesis import given, assume, settings, strategies as st

# pylint: disable=missing-class-docstring,missing-function-docstring,invalid-name


@dataclass
class Small:
    my_list_int: List[int]


@dataclass
class Big:
    my_int: int
    my_str: str
    my_float: float
    my_list_small: List["Small"]
    my_optional_str: Optional[str]
    my_list_of_small_or_str: List[Union[Small, str]]
    my_list: List


SmallData = st.fixed_dictionaries({"my_list_int": st.lists(st.integers())})
BigData = st.fixed_dictionaries(
    {
        "my_int": st.integers(),
        "my_str": st.text(),
        "my_float": st.floats(),
        "my_list_small": st.lists(SmallData),
        "my_list_of_small_or_str": st.lists(st.one_of(SmallData, st.text())),
        "my_list": st.lists(st.text()),
    },
    optional={"my_optional_str": st.one_of(st.text(), st.none())},
)


@given(BigData)
def test_serde_big_data(big_data: dict):
    deserialized = deserialize(big_data, Big)
    assert deserialized.my_int == big_data["my_int"]
    assert deserialized.my_list == big_data["my_list"]
    assert deserialized.my_list_of_small_or_str == [
        Small(**value) if isinstance(value, dict) else value
        for value in big_data["my_list_of_small_or_str"]
    ]
    print("my_optional_str" in big_data, deserialized.my_optional_str)
    serialized = serialize(deserialized)
    assert serialized == {
        **{"my_optional_str": None,},
        **big_data,
    }

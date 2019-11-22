"""Test the deserialize class"""

from dataclasses import dataclass
from typing import Dict, List, Union, Optional, NamedTuple

from serdataclasses.deserialize import deserialize
from serdataclasses.serialize import serialize

from hypothesis import given, assume, settings, strategies as st

# pylint: disable=missing-class-docstring,missing-function-docstring,invalid-name


class SmallNamedTuple(NamedTuple):
    my_list_int: List[float]


@dataclass
class SmallDataClass:
    my_list_int: List[int]


@dataclass
class Big:
    my_int: int
    my_str: str
    my_float: float
    my_list_small: List["SmallNamedTuple"]
    my_optional_str: Optional[str]
    my_list_of_small_or_str: List[Union[SmallDataClass, str]]
    my_list: List
    my_dict: Dict[int, SmallDataClass]


SMALL_DATA_DC = st.fixed_dictionaries({"my_list_int": st.lists(st.integers())})
SMALL_DATA_NT = st.fixed_dictionaries({"my_list_int": st.lists(st.floats())})
BIG_DATA = st.fixed_dictionaries(
    {
        "my_int": st.integers(),
        "my_str": st.text(),
        "my_float": st.floats(),
        "my_list_small": st.lists(SMALL_DATA_NT),
        "my_list_of_small_or_str": st.lists(
            st.one_of(SMALL_DATA_DC, st.text())
        ),
        "my_list": st.lists(st.text()),
        "my_dict": st.dictionaries(st.integers(), SMALL_DATA_DC),
    },
    optional={"my_optional_str": st.one_of(st.text(), st.none())},
)


@given(BIG_DATA)
def test_serde_big_data(big_data: dict):
    deserialized = deserialize(big_data, Big)
    assert deserialized.my_int == big_data["my_int"]
    assert deserialized.my_list == big_data["my_list"]
    assert deserialized.my_list_small == [
        SmallNamedTuple(**value) for value in big_data["my_list_small"]
    ]
    assert deserialized.my_list_of_small_or_str == [
        SmallDataClass(**value) if isinstance(value, dict) else value
        for value in big_data["my_list_of_small_or_str"]
    ]
    assert deserialized.my_dict == {
        key: SmallDataClass(**value)
        for key, value in big_data["my_dict"].items()
    }
    serialized = serialize(deserialized)
    assert serialized == {
        **{"my_optional_str": None},
        **big_data,
    }

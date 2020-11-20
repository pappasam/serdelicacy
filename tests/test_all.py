"""Test the deserialize class."""

from dataclasses import dataclass
from typing import Dict, List, NamedTuple, Optional, Tuple, TypedDict, Union

from hypothesis import given
from hypothesis import strategies as st

from serdelicacy import UNDEFINED, OptionalProperty, dump, load

# pylint: disable=missing-class-docstring,missing-function-docstring,invalid-name
# pylint: disable=too-many-instance-attributes


class SmallTypedDict(TypedDict):
    my_value: int


class SmallNamedTuple(NamedTuple):
    my_list_int: List[float]


class SmallNamedTupleSingular(NamedTuple):
    my_value: int
    my_default: str = "hello"


@dataclass
class SmallDataClass:
    my_list_int: List[int]


@dataclass
class Big:
    my_int: int
    my_str: str
    my_float: float
    my_named_tuple: SmallNamedTupleSingular
    my_list_small: List["SmallNamedTuple"]
    my_optional_str: OptionalProperty[Optional[str]]
    my_list_of_small_or_str: List[Union[SmallDataClass, str]]
    my_list: List
    my_dict: Dict[int, SmallDataClass]
    my_typed_dict: SmallTypedDict
    my_tuple: Tuple[int, str]
    my_tuple_long: Tuple[int, ...]
    my_default: str = "default_value"
    my_default_with_value: str = "default_value"


SMALL_DATA_TD = st.fixed_dictionaries({"my_value": st.integers()})
SMALL_DATA_DC = st.fixed_dictionaries({"my_list_int": st.lists(st.integers())})
SMALL_DATA_NT = st.fixed_dictionaries({"my_list_int": st.lists(st.floats())})
SMALL_DATA_NT_SING = st.fixed_dictionaries({"my_value": st.integers()})
BIG_DATA = st.fixed_dictionaries(
    {
        "my_int": st.integers(),
        "my_str": st.text(),
        "my_float": st.floats(),
        "my_named_tuple": SMALL_DATA_NT_SING,
        "my_list_small": st.lists(SMALL_DATA_NT),
        "my_list_of_small_or_str": st.lists(
            st.one_of(SMALL_DATA_DC, st.text())
        ),
        "my_list": st.lists(st.text()),
        "my_dict": st.dictionaries(st.integers(), SMALL_DATA_DC),
        "my_typed_dict": SMALL_DATA_TD,
        "my_tuple": st.tuples(st.integers(), st.text()),
        "my_tuple_long": st.tuples(
            st.integers(), st.integers(), st.integers()
        ),
        "my_default_with_value": st.text(),
    },
    optional={"my_optional_str": st.one_of(st.text(), st.none())},
)


@given(BIG_DATA)
def test_serde_big_data(big_data: dict):
    deserialized = load(big_data, Big)
    assert deserialized.my_default == "default_value"
    assert (
        deserialized.my_default_with_value == big_data["my_default_with_value"]
    )
    assert deserialized.my_named_tuple.my_default == "hello"
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
    assert deserialized.my_typed_dict == big_data["my_typed_dict"]
    assert deserialized.my_tuple == big_data["my_tuple"]
    assert deserialized.my_tuple_long == big_data["my_tuple_long"]
    if "my_optional_str" in big_data:
        assert deserialized.my_optional_str == big_data["my_optional_str"]
    else:
        assert deserialized.my_optional_str is UNDEFINED
    serialized = dump(deserialized)
    assert serialized == {
        "my_default": "default_value",
        **big_data,
        **{
            "my_tuple": list(deserialized.my_tuple),
            "my_tuple_long": list(deserialized.my_tuple_long),
        },
        "my_named_tuple": {
            "my_value": deserialized.my_named_tuple.my_value,
            "my_default": "hello",
        },
    }

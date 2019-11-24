# serdataclasses

[![image-version](https://img.shields.io/pypi/v/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image-license](https://img.shields.io/pypi/l/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image](https://img.shields.io/pypi/pyversions/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image-ci](https://github.com/pappasam/serdataclasses/workflows/serdataclasses%20ci/badge.svg)](https://github.com/pappasam/serdataclasses/actions?query=workflow%3A%22serdataclasses+ci%22)

This library has the following goals:

1. "Deserialize" unstructured Python types into structured, type-hinted Python types (dataclasses.dataclass, typing.NamedTuples).
2. "Serialize" structured, type-hinted Python objects into unstructured Python types (eg, the reverse)
3. Provide the user clear error messages in the event that serde fails.
4. Require no type changes on the part of the user. No need to give your containers a special type to help this library perform serde, it works out of the box.
5. Work correctly for all forms of NamedTuples and dataclasses. Unfortunately, prior to Python 3.8, the dataclasses had some deficiencies. Mainly, `dataclasses.InitVar` was a singleton whose contained type could not be inspected at runtime. For this reason, only Python 3.8+ is supported.

No external dependencies. Python 3.8+.

## Installation

```bash
# With pip
pip install serdataclasses

# With poetry
poetry add serdataclasses
```

## Usage

```python
import dataclasses
import typing
import serdataclasses

@dataclasses.dataclass
class SmallContainer:
    my_str: str

@dataclasses.dataclass
class BigContainer:
    my_int: int
    my_list: typing.List[SmallContainer]

MY_DATA = {
    "my_int": 1,
    "my_list": [
        { "my_str": "rawr" },
        { "my_str": "woof" },
    ],
}

# Deserialization
MY_STRUCTURED_DATA = serdataclasses.load(MY_DATA, BigContainer)
print("Deserialization:", MY_STRUCTURED_DATA)

# Serialization
MY_UNSTRUCTURED_DATA_AGAIN = serdataclasses.dump(MY_STRUCTURED_DATA)
print("Serialization:", MY_UNSTRUCTURED_DATA_AGAIN)
```

Result:

```console
Deserialization: BigContainer(my_int=1, my_list=[SmallContainer(my_str='rawr'), SmallContainer(my_str='woof')])
Serialization: {'my_int': 1, 'my_list': [{'my_str': 'rawr'}, {'my_str': 'woof'}]}
```

## Local Development

Local development for this project is quite simple.

**Dependencies**

Install the following tools manually.

* [Poetry](https://github.com/sdispater/poetry#installation)
* [GNU Make](https://www.gnu.org/software/make/)

*Recommended*

* [asdf](https://github.com/asdf-vm/asdf)

**Set up development environment**

```bash
make setup
```

**Run Tests**

```bash
make test
```

## Notes

* Initially inspired by [undictify](https://github.com/Dobiasd/undictify) and a PR I helped with. serdataclasses's goals are different; it's exclusively focused on serde instead of general function signature overrides.
* I also notice some striking similarities with a library called [typedload](https://github.com/ltworf/typedload) (great minds think alike, I guess :p). I renamed my top-level functions to "load" and "dump" in typedload's homage. Unfortunately, as of version `1.20`, typedload does not handle all types of dataclasses elegantly (mainly, InitVar). Since typedload supports Python 3.5+, it never will elegantly handle all dataclasses without lots of unfortunate conditionals in the codebase. If you must use Python 3.7-, I suggest looking into typedload.

## Written by

Samuel Roeca *samuel.roeca@gmail.com*

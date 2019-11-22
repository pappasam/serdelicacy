# serdataclasses

[![image-version](https://img.shields.io/pypi/v/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image-license](https://img.shields.io/pypi/l/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image](https://img.shields.io/pypi/pyversions/serdataclasses.svg)](https://python.org/pypi/serdataclasses)

This library has two goals:

1. "Deserialize" unstructured Python types into structured, type-hinted Python types (dataclasses.dataclass, typing.NamedTuples).
2. "Serialize" structured, type-hinted Python objects into unstructured Python types (eg, the reverse)

It has no external dependencies. Python 3.8+.

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
print(MY_STRUCTURED_DATA)

# Serialization
MY_UNSTRUCTURED_DATA_AGAIN = serdataclasses.dump(MY_STRUCTURED_DATA)
print(MY_UNSTRUCTURED_DATA_AGAIN)
```

Result:

```console
BigContainer(my_int=1, my_list=[SmallContainer(my_str='rawr'), SmallContainer(my_str='woof')])
{'my_int': 1, 'my_list': [{'my_str': 'rawr'}, {'my_str': 'woof'}]}
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

* Inspired by [undictify](https://github.com/Dobiasd/undictify), but special-cased to dataclasses and more-focused on serde instead of general function signature overrides.

## Written by

Samuel Roeca *samuel.roeca@gmail.com*

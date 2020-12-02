# serdelicacy

[![image-version](https://img.shields.io/pypi/v/serdelicacy.svg)](https://python.org/pypi/serdelicacy)
[![image-license](https://img.shields.io/pypi/l/serdelicacy.svg)](https://python.org/pypi/serdelicacy)
[![image](https://img.shields.io/pypi/pyversions/serdelicacy.svg)](https://python.org/pypi/serdelicacy)
[![image-ci](https://github.com/pappasam/serdelicacy/workflows/serdelicacy%20ci/badge.svg)](https://github.com/pappasam/serdelicacy/actions?query=workflow%3A%22serdelicacy+ci%22)

Serialize (`serdelicacy.dump`) and deserialize (`serdelicacy.load`) from/to strongly-typed, native Python data structures.

## Features

1. Effortless deserialization of unstructured Python types into structured, type-hinted Python types (`dataclasses.dataclass`, `typing.NamedTuple`)
2. Effortless serialization of structured, type-hinted Python objects into unstructured Python types (eg, the reverse)
3. Clear error messages when serde fails at runtime
4. No inherited, non-standard types. dataclasses, NamedTuples, and other standard Python types are bread and butter
5. Editor support: I like my autocompletion, so I jump through lots of hoops to make this library compatible with Jedi
6. Handle [optional properties](https://www.typescriptlang.org/docs/handbook/interfaces.html#optional-properties) with a domain-specific `serdelicacy.OptionalProperty`
7. Enable customization through sophisticated validation, deserialization overrides, and serialization overrides for dataclasses.
8. Require no 3rd party dependencies; Python 3.8+

## Installation

```bash
# With pip
pip install serdelicacy

# With poetry
poetry add serdelicacy
```

## Usage

See [examples folder](https://github.com/pappasam/serdelicacy/tree/master/example).

## Validation / transformation for dataclasses

Customization override options are available for validations and transformations on both deserialization and serialization. Custom overrides are available for `dataclasses` through the `metadata` argument to the `dataclasses.field` function:

```python
from dataclasses import dataclass, field

import serdelicacy
from serdelicacy import Override

def _is_long_enough(value) -> None:
    if len(value) < 4:
        raise ValueError(f"'{value}' is not enough characters")

VALUE = {"firstname": "richard", "lastname": "spencerson"}

@dataclass
class Person:
    firstname: str = field(
        metadata={
            "serdelicacy": Override(
                validate=_is_long_enough,
                transform_load=str.title,
            )
        }
    )
    lastname: str = field(
        metadata={
            "serdelicacy": Override(
                validate=_is_long_enough,
                transform_load=str.title,
                transform_dump=str.upper,
            )
        }
    )

print(serdelicacy.load(VALUE, Person))
```

As suggested by the Python [dataclasses.field documentation](https://docs.python.org/3/library/dataclasses.html#dataclasses.field), all `serdelicacy`-related field metadata is namespaced to 1 dictionary key: `serdelicacy`. Its value should be of type `serdelicacy.Override`, a dataclass itself whose fields are the following:

- `validate`: `Callable[[Any], NoReturn], Callable[[Any], bool]`: a function that either a) returns a boolean where False indicates failed validation or b) nothing, but raises Python exceptions on validation failure. Is executed as the final step of a value's load, after all transformations have been completed. By default, this is a function that does nothing.
- `transform_load`: `Callable[[Any], Any]`. This transformation is executed before any other loading takes place. By default, this is an [identity function](https://en.wikipedia.org/wiki/Identity_function)
- `transform_postload`: this should be `Callable[[T], T]]`, where `T` is the type of the field. This transformation is executed after all recursive loading takes place as the final step before the value is returned for upstream processing. By default, this is an [identity function](https://en.wikipedia.org/wiki/Identity_function)
- `transform_dump`: this should be `Callable[[T], Any]]`, where `T` is the type of the field. This function is executed before a value is recursively serialized. By default, this is an [identity function](https://en.wikipedia.org/wiki/Identity_function)

Finally, you may not need to use these tools initially, but if you have strict validation or transformation requirements on your project, you'll be extremely happy they're here

## FAQ

### My JSON keys contain whitespace, etc

Simple solution: use `typeing.TypeDict`'s [backwards-compatibility syntax](https://www.python.org/dev/peps/pep-0589/#alternative-syntax).

```python
from pprint import pprint
from typing import List, TypedDict

import serdelicacy
from serdelicacy import OptionalProperty

DATA = [
    {
        "weird, key": 1,
        "normal": 2,
    },
    {
        "normal": 3,
    },
]

DataItem = TypedDict(
    "DataItem",
    {
        "weird, key": OptionalProperty[int],
        "normal": int,
    },
)

LOADED = serdelicacy.load(DATA, List[DataItem])

print("Loaded data:")
pprint(LOADED)

print("Re-serialized data:")
pprint(serdelicacy.dump(LOADED))
```

This prints the following to the console.

```text
Loaded data:
[{'normal': 2, 'weird, key': 1},
 {'normal': 3, 'weird, key': <Missing property>}]
Re-serialized data:
[{'normal': 2, 'weird, key': 1}, {'normal': 3}]
```

Try changing values in your JSON data; you'll get runtime errors if your data does not conform to the above schema. Additionally, `mypy` should call out any misused variable keys / types. In short, this has enabled a type-safe load and a perfectly sane dump.

## Local Development

Local development for this project is simple.

**Dependencies**

Install the following tools manually.

- [Poetry](https://github.com/sdispater/poetry#installation)
- [GNU Make](https://www.gnu.org/software/make/)

_Recommended_

- [asdf](https://github.com/asdf-vm/asdf)

**Set up development environment**

```bash
make setup
```

**Run Tests**

```bash
make test
```

## Notes

- Initially inspired by [undictify](https://github.com/Dobiasd/undictify) and a PR I helped with. serdelicacy's goals are different; it's focused on serde instead of general function signature overrides.
- I also notice some striking similarities with a library called [typedload](https://github.com/ltworf/typedload) (great minds think alike, I guess :p). I renamed my top-level functions to "load" and "dump" in typedload's homage. Unfortunately, as of version `1.20`, typedload does not handle all types of dataclasses elegantly (mainly, InitVar). Since typedload supports Python 3.5+, it never will elegantly handle all dataclasses without lots of unfortunate conditionals in the codebase. If you must use Python 3.7-, I suggest looking into typedload.

## Written by

Samuel Roeca *samuel.roeca@gmail.com*

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

See [examples folder](https://github.com/pappasam/serdelicacy/tree/master/example) if you'd like to get your hands dirty. Otherwise, keep reading for a complete, real-world example.

### Example: Libraries and Books

Assume that you receive a `JSON` list of libraries containing each library's name and a list of each library's books.

```json
[
  {
    "name": "Clark County Library",
    "books": [
      {
        "title": "Hello, World!",
        "author": "Susy Smith",
        "year": 1929,
        "tags": ["boring"]
      },
      {
        "title": "The great showman",
        "author": "Beth John"
      },
      {
        "title": "My favorite pony",
        "author": null
      }
    ]
  },
  {
    "name": "Only 1 book here",
    "books": [
      {
        "title": "The great fun time",
        "author": "Smitty",
        "year": 1950,
        "tags": ["swell"]
      }
    ]
  }
]
```

Now you want to ingest this document into Python. Your first step is probably to deserialize the JSON string (or file) into Python data structures.

```python
import json
from pprint import pprint

with open("libraries.json", "r") as infile:
    libraries_raw = json.load(infile)

pprint(libraries_raw)
print(type(libraries_raw))
print(type(libraries_raw[0]))
```

Assuming the JSON is read from a file called `libraries.py`, the preceding script will print:

```text
[{'books': [{'author': 'Susy Smith',
             'tags': ['boring'],
             'title': 'Hello, World!',
             'year': 1929},
            {'author': 'Beth John', 'title': 'The great showman'},
            {'author': None, 'title': 'My favorite pony'}],
  'name': 'Clark County Library'},
 {'books': [{'author': 'Smitty',
             'tags': ['swell'],
             'title': 'The great fun time',
             'year': 1950}],
  'name': 'Only 1 book here'}]
<class 'list'>
<class 'dict'>
```

Some observations:

1. Python's native `json` module deserializes the JSON string / document into Python's primitive (or primitive-like) types
2. `null` is translated to Python's `None`
3. The first list element is a dictionary. So Python appears to have translated the JSON into a list of dictionaries.
4. There is little inherent structure to the Python objects deserialized by the JSON module. By this, I mean that we have no way of knowing whether the dictionaries contain keys that we expect or are structured improperly. Should books also have an `"isbn"` field? Does code we write that uses `libraries_raw` expect an `"isbn"` field? What happens if there are missing tags?

The first 3 items are merely facts; `serdelicacy` accepts these facts and builds on them. The 4th item in this list is THE problem that `serdelicacy` is designed to solve. If we take the above Python dictionary and associate it with a Python variable named `LIBRARIES`, we can define a strongly-typed Python container that `serdelicacy` can use to ingest `LIBRARIES`.

```python
from dataclasses import dataclass, field
from pprint import pprint
from typing import List, Optional

import serdelicacy
from serdelicacy import OptionalProperty

[
    {
        "books": [
            {
                "author": "Susy Smith",
                "tags": ["boring"],
                "title": "Hello, World!",
                "year": 1929,
            },
            {"author": "Beth John", "title": "The great showman"},
            {"author": None, "title": "My favorite pony"},
        ],
        "name": "Clark County Library",
    },
    {
        "books": [
            {
                "author": "Smitty",
                "tags": ["swell"],
                "title": "The great fun time",
                "year": 1950,
            }
        ],
        "name": "Only 1 book here",
    },
]

@dataclass
class Book:
    author: Optional[str]
    title: str
    year: OptionalProperty[int]
    tags: List[str] = field(default_factory=list)

@dataclass
class Library:
    books: List[Book]
    name: str

LIBRARIES_LOADED = serdelicacy.load(LIBRARIES, List[Library])
print(LIBRARIES_LOADED[0].name)
print(LIBRARIES_LOADED[0].books[1].author)
pprint(serdelicacy.dump(LIBRARIES_LOADED))
```

Running the above script, we get the following output to the terminal:

```text
[{'books': [{'author': 'Susy Smith',
             'tags': ['boring'],
             'title': 'Hello, World!',
             'year': 1929},
            {'author': 'Beth John', 'tags': [], 'title': 'The great showman'},
            {'author': None, 'tags': [], 'title': 'My favorite pony'}],
  'name': 'Clark County Library'},
 {'books': [{'author': 'Smitty',
             'tags': ['swell'],
             'title': 'The great fun time',
             'year': 1950}],
  'name': 'Only 1 book here'}]
```

Notice how we have the following features:

1. Data structures are loaded, recursively, without you needing to write anything more than a couple standard Python classes.
2. For missing properties / dictionary keys (for example, `Book.tags`), we can set a default value in our dataclass using standard Python and `serdelicacy` adds the default value to our structure
3. For missing properties without default values, serdelicacy intelligently omits them when re-serializing the result. There is also an option to `serdelicacy.load` that allows you to convert missing values to `None` and keep the keys in the output. For all other desired default values, just use `dataclasses.field`; no need to re-invent the wheel!

What about additional validation, you may ask? Again, just use dataclasses! Assume that, for some reason, no book can possibly be published before 1930, and that a book published before 1930 invalidates all data. No problem, you can do 1 of 2 things:

1. Just use the standard method `__post_init__` on the relevant dataclass!
2. Use `dataclasses.field` and put a function in the dictionary's "validate" key. The provided function should either return `True` on positive validation / `False` on non-validation, or nothing at all and instead rely on the raising of exceptions to indicate whether validation passed for failed.

```python
from dataclasses import dataclass, field
from pprint import pprint
from typing import List, Optional

import serdelicacy
from serdelicacy import OptionalProperty

LIBRARIES = [
    {
        "books": [
            {
                "author": "Susy Smith",
                "tags": ["boring"],
                "title": "Hello, World!",
                "year": 1929,
            },
            {"author": "Beth John", "title": "The great showman"},
            {"author": None, "title": "My favorite pony"},
        ],
        "name": "Clark County Library",
    },
    {
        "books": [
            {
                "author": "Smitty",
                "tags": ["swell"],
                "title": "The great fun time",
                "year": 1950,
            }
        ],
        "name": "Only 1 book here",
    },
]

@dataclass
class Book:
    author: Optional[str]
    title: str = field(metadata={"validate": str.istitle})
    year: OptionalProperty[int]
    tags: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        if self.year and self.year < 1930:
            raise ValueError(
                f"Received illegal year {self.year}, cannot be before 1930"
            )

@dataclass
class Library:
    books: List[Book]
    name: str

LIBRARIES_LOADED = serdelicacy.load(LIBRARIES, List[Library])
```

Running this script should give you a clear error message containing a description of the first error encountered, along with each intermediate object in its recursive chain to help you debug further. This structure makes it incredibly easy to see not only what your error is, but where it occurred in both the data `serdelicacy.load` receives but also in the types `serdelicacy.load` uses to attempt to deserialize the received data.

In serde, when working with resources external to your system, errors are inevitable. These error messages should hopefully make debugging your errors less annoying.

## Validation / transformation for dataclasses

The following customization options are available for validation, deserialization overrides, and serialization overrides. `dataclasses` customization relies on the `metadata` argument to the `dataclasses.field` function:

```python
from dataclasses import dataclass, field
import serdelicacy

def _is_long_enough(value) -> None:
    if len(value) < 4:
        raise ValueError(f"'{value}' is not enough characters")

VALUE = {"firstname": "richard", "lastname": "spencerson"}

@dataclass
class Person:
    firstname: str = field(
        metadata={
            "validate": _is_long_enough,
            "transform_load": str.title,
        }
    )
    lastname: str = field(
        metadata={
            "validate": _is_long_enough,
            "transform_load": str.title,
            "transform_dump": str.upper,
        }
    )

print(serdelicacy.load(VALUE, Person))
```

Here are the following `metadata` keys that `serdelicacy` considers, if present:

- `"validate"`: if provided, this should be `Callable[[Any], NoReturn], Callable[[Any], bool]`: a function that either a) returns a boolean where False indicates failed validation or b) nothing, but raises Python exceptions on validation failure. Is executed as the final step of a value's load, after all transformations have been completed.
- `"transform_load"`: if provided, this should be, at minimum, `Callable[[Any], Any]`. This transformation is executed before any other loading takes place.
- `"transform_postload"`: if provided, this should be `Callable[[T], T]]`, where `T` is the type of the field. This transformation is executed after all recursive loading takes place as the final step before the value is returned for upstream processing.

You may not need to use these tools initially, but if you have strict validation or transformation requirements on your project, you'll be extremely happy they're here!

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

# serdataclasses

[![image-version](https://img.shields.io/pypi/v/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image-license](https://img.shields.io/pypi/l/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image](https://img.shields.io/pypi/pyversions/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image-ci](https://github.com/pappasam/serdataclasses/workflows/serdataclasses%20ci/badge.svg)](https://github.com/pappasam/serdataclasses/actions?query=workflow%3A%22serdataclasses+ci%22)

Serialize (`serdataclasses.dump`) from and deserialize (`serdataclasses.load`) to strongly-typed, native Python data structures.

## Motivation

No typing-focused [serde](https://en.wikipedia.org/wiki/Serialization) library in Python satisfies me. Call me needy, but when I translate between loosely-typed data structures like `list` and `dict` into strongly-typed data structures like `NamedTuple` and `dataclasses.dataclass`, I want the following capabilities:

1. Effortlessl deserialization of unstructured Python types into structured, type-hinted Python types (`dataclasses.dataclass`, `typing.NamedTuple`)
2. Effortless serialization of structured, type-hinted Python objects into unstructured Python types (eg, the reverse)
3. Clear error messages when serde fails at runtime
4. No inherited, non-standard types. dataclasses, NamedTuples, and other standard Python types are bread and butter
5. Editor support: I like my autocompletion, so I jump through lots of hoops to make this library compatible with Jedi
6. Handle [optional properties](https://www.typescriptlang.org/docs/handbook/interfaces.html#optional-properties) with a domain-specific `serdataclasses.OptionalProperty`
7. Provide option to automatically convert primitive types, but avoid converting ambiguous types (`Union`, `TypeVar`, etc). Handle of `Optional` and `serdataclasses.OptionalProperty`
8. Require no 3rd party dependencies; Python 3.8+

## Installation

```bash
# With pip
pip install serdataclasses

# With poetry
poetry add serdataclasses
```

## Usage

See [examples folder](example) if you'd like to get your hands dirty. Otherwise, keep reading for a complete, real-world example.

### Example: Libraries and Books

Assume that, from an external API, you receive a `JSON` list of libraries containing the library name and a list of books that each library currently has.

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

Now you want to ingest this document into Python. Your first step is probably to deserialize the JSON string (or file) into Python data structures. Assuming the JSON is read from a file called `libraries.py`, the following script will print the following:

```python
import json
from pprint import pprint

with open("libraries.json", "r") as infile:
    libraries_raw = json.load(infile)

pprint(libraries_raw)
print(type(libraries_raw))
print(type(libraries_raw[0]))
```

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

The first 3 items are merely facts; `serdataclasses` accepts these facts and builds on them. The 4th item in this list is THE problem that `serdataclasses` is designed to solve. If we take the above Python dictionary associate it with a Python variable `LIBRARIES`, we can define a container for use with `serdataclasses` to ingest `LIBRARIES` into a strongly-typed Python container.

```python
from dataclasses import dataclass, field
from pprint import pprint
from typing import List, Optional

import serdataclasses
from serdataclasses import OptionalProperty

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

LIBRARIES_LOADED = serdataclasses.load(LIBRARIES, List[Library])
print(LIBRARIES_LOADED[0].name)
print(LIBRARIES_LOADED[0].books[1].author)
pprint(serdataclasses.dump(LIBRARIES_LOADED))
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
2. For missing properties / dictionary keys (for example, `Book.tags`), we can set a default value in our dataclass using standard Python and `serdataclasses` adds the default value to our structure
3. For missing properties without default values, serdataclasses intelligently omits them when re-serializing the result. There is also an option to `serdataclasses.load` that allows you to convert missing values to `None` and keep the keys in the output. For all other desired default values, just use `dataclasses.field`; no need to re-invent the wheel!

What about additional validation, you may ask? Again, just use dataclasses! Assume that, for some reason, no book can possibly be published before 1930, and that a book published before 1930 invalidates all data. No problem, just use the standard method `__post_init__` on the relevant dataclass!

```python
from dataclasses import dataclass, field
from pprint import pprint
from typing import List, Optional

import serdataclasses
from serdataclasses import OptionalProperty

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
    title: str
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

LIBRARIES_LOADED = serdataclasses.load(LIBRARIES, List[Library])
```

Running this script should give you the following error message (traceback omitted because it can get somewhat long)

```text
serdataclasses.errors.DeserializeError: Received illegal year 1929, cannot be before 1930
  4. "<class '__main__.Book'>": "{'author': 'Susy Smith', 'tags': ['boring'], 'title': 'Hello, World!', 'year': 1929}"
  3. 'typing.List[__main__.Book]': "[{'author': 'Susy Smith', 'tags': ['boring'], 'title': 'Hello, World!', 'year': 1929}, {'author': 'Beth John', 'title': 'The great showman'}, {'author': None, 'title': 'My favorite pony'}]"
  2. "<class '__main__.Library'>": "{'books': [{'author': 'Susy Smith', 'tags': ['boring'], 'title': 'Hello, World!', 'year': 1929}, {'author': 'Beth John', 'title': 'The great showman'}, {'author': None, 'title': 'My favorite pony'}], 'name': 'Clark County Library'}"
  1. 'typing.List[__main__.Library]': "[{'books': [{'author': 'Susy Smith', 'tags': ['boring'], 'title': 'Hello, World!', 'year': 1929}, {'author': 'Beth John', 'title': 'The great showman'}, {'author': None, 'title': 'My favorite pony'}], 'name': 'Clark County Library'}, {'books': [{'author': 'Smitty', 'tags': ['swell'], 'title': 'The great fun time', 'year': 1950}], 'name': 'Only 1 book here'}]"
```

The error message begins with the error message received, followed by a reverse presention container types paired with the data they attempted to deserialize. This structure makes it incredibly easy to see not only what your error is, but where exactly it occured in both the data `serdataclasses.load` receives but also in the types `serdataclasses.load` uses to attempt to deserialize the received data.

In serde, when working with resources external to your system, errors are inevitable. These error messages should hopefully make debugging your errors less annoying.

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

- Initially inspired by [undictify](https://github.com/Dobiasd/undictify) and a PR I helped with. serdataclasses's goals are different; it's focused on serde instead of general function signature overrides.
- I also notice some striking similarities with a library called [typedload](https://github.com/ltworf/typedload) (great minds think alike, I guess :p). I renamed my top-level functions to "load" and "dump" in typedload's homage. Unfortunately, as of version `1.20`, typedload does not handle all types of dataclasses elegantly (mainly, InitVar). Since typedload supports Python 3.5+, it never will elegantly handle all dataclasses without lots of unfortunate conditionals in the codebase. If you must use Python 3.7-, I suggest looking into typedload.

## Written by

Samuel Roeca *samuel.roeca@gmail.com*

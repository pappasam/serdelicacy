# serdataclasses

[![image-version](https://img.shields.io/pypi/v/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image-license](https://img.shields.io/pypi/l/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image](https://img.shields.io/pypi/pyversions/serdataclasses.svg)](https://python.org/pypi/serdataclasses)
[![image-ci](https://github.com/pappasam/serdataclasses/workflows/serdataclasses%20ci/badge.svg)](https://github.com/pappasam/serdataclasses/actions?query=workflow%3A%22serdataclasses+ci%22)

This library has the following goals:

1. "Deserialize" unstructured Python types into structured, type-hinted Python types (`dataclasses.dataclass`, `typing.NamedTuple`).
2. "Serialize" structured, type-hinted Python objects into unstructured Python types (eg, the reverse)
3. Provide the user with clear error messages when serde fails.
4. Require no type changes on the part of the user. No need to give your containers a special type to help this library perform serde, it works out of the box.
5. Support all `NamedTuple`s and `dataclass`es. Before Python 3.8, `dataclasses.InitVar` was a singleton with an opaque runtime type. Because of this deficiency, we support Python 3.8+.
6. Sanely support [optional properties](https://www.typescriptlang.org/docs/handbook/interfaces.html#optional-properties) with a domain-specific `OptionalProperty`.
7. Provide option to automatically convert primitive types, but avoid converting ambiguous types (`Union`, `TypeVar`, etc). Handle the special cases of `Optional` and `OptionalProperty`.
8. Require no 3rd party dependencies.

## Installation

```bash
# With pip
pip install serdataclasses

# With poetry
poetry add serdataclasses
```

## Usage

See [examples folder](example).

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

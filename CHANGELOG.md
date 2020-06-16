# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.6.1

### Fixed

- `object` types were incorrectly specified, they have been changed to `Any`.
- Update pylint and mypy for local debugging purposes

## 0.6.0

### Added

- Support default arguments for `NamedTuples` and `dataclasses`. Behavior: if default argument exists, if no argument is present in the unstructure Python object, and if there is a default value for the argument, we use the default argument instead of `None` (which is automatically returned by `dict.get`).

## 0.5.1

There are no functional changes here, just some book-keeping CI / local dev-related stuff.

### Added

- Set up continuous integration using GitHub Actions.

### Fixed

- Some development dependencies weren't in pyproject.toml.

## 0.5.0

### Added

- `load` now supports `tuple` types
- `dump` now supports Sequence/Mapping, not just list/dict

## 0.4.0

### Added

- Keywords and classifiers to `pyproject.toml`.

### Changed

- Lists and Dicts in `deserialize.load` have been generalized into the generic protocols `typing.Sequence` and `typing.Mapping`.
- `typing.get_origin` and `typing.get_args` are now call called only once in the Deserialize constructor.

## 0.3.0

### Added

- Support for `typing.TypedDict`
- `typesafe_constructor` argument to `deserialize.load` to optionally ensure type safety at the top-level. It defaults to True.

## 0.2.0

### Added

- This `CHANGELOG.md`
- `deserialize.load`, `deserialize.DeserializeError`, and `serialize.dump` are imported at the top-level.
- Support for NamedTuple and Dict
- Add `py.typed` to package (PEP 561)
- `typedefs.NoResult` and `typedefs.Possible`. This is a bespoke `typing.Optional` implementation because `None` is a value we actually care about.

### Changed

- `deserialize.deserialize` changed to `deserialize.load`
- `serialize.serialize` changed to `serialize.dump`
- The `deserialize._deserialize` function is replaced by `deserialize.Deserialize`.
- Removed "vaporware" designation: this is now a real project.

### Fixed

- `mypy`, `pylint`, `black`, `toml-sort`, and `isort` all pass.

### Removed

- Recursive types. I may add them again in the future when `mypy` supports them, but given the sketchyness of the type system at present, I'm not confident that they'll actually help

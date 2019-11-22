# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## 0.2.0

### Added

* This `CHANGELOG.md`
* `deserialize.load`, `deserialize.DeserializeError`, and `serialize.dump` are imported at the top-level.
* Support for NamedTuple and Dict
* Add `py.typed` to package (PEP 561)
* `typedefs.NoResult` and `typedefs.Possible`. This is a bespoke `typing.Optional` implementation because `None` is a value we actually care about.

### Changed

* `deserialize.deserialize` changed to `deserialize.load`
* `serialize.serialize` changed to `serialize.dump`
* The `deserialize._deserialize` function is replaced by `deserialize.Deserialize`.
* Removed "vaporware" designation: this is now a real project.

### Fixed

* `mypy`, `pylint`, `black`, `toml-sort`, and `isort` all pass.

### Removed

* Recursive types. I may add them again in the future when `mypy` supports them, but given the sketchyness of the type system at present, I'm not confident that they'll actually help

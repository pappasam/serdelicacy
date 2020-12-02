"""Dump strongly-typed containers into loosely-typed objects."""

from dataclasses import asdict, fields, is_dataclass
from typing import Any, Mapping, Sequence

from .overrides import get_override
from .typedefs import MISSING, NamedTupleType


def _filter_keep(value: Any, keep_always: bool) -> bool:
    """Determine whether we should keep a value in serialized output."""
    if keep_always:
        return True
    return value is not MISSING


def _identity(value: Any) -> Any:
    """Simple identity function, returning original value."""
    return value


def dump(obj: Any, convert_missing_to_none: bool = False) -> Any:
    """Serialize the object into a less-typed form.

    If serializing a dataclass and `transform_dump` metadata exists in a
    `dataclasses.field`, its value is assumed to be function whose result is
    serialized before being passed recursively down the chain.

    :param convert_missing_to_none: retain missing property's key and convert
        its value to None. This will keep all keys when serializing, useful if
        you want to keep all column names and assign value of `None` to missing
        columns.

    Serialize from: - `x` -> `y`:
      - `dataclass` -> `Dict`
      - `NamedTuple` -> `Dict`
      - `str` -> `str`
      - `Sequence` -> `List`
      - `Mapping` -> `Dicts`
      * if `convert_missing_to_none` is True:
        - `MISSING` -> `None`
      * else
        - `MISSING` keys are filtered out and missing values are kept as-is
      - `Anything else` -> `itself`
    """
    # pylint: disable=too-many-return-statements
    if is_dataclass(obj):
        custom_dump = {
            f.name: get_override(f.metadata.get("serdelicacy"))
            for f in fields(obj)
        }
        return {
            key: dump(__value_converted, convert_missing_to_none)
            for key, value in asdict(obj).items()
            if _filter_keep(
                (__value_converted := custom_dump[key].transform_dump(value)),
                convert_missing_to_none,
            )
        }
    if isinstance(obj, NamedTupleType):
        return {
            key: dump(value, convert_missing_to_none)
            for key, value in obj._asdict().items()
            if _filter_keep(value, convert_missing_to_none)
        }
    if isinstance(obj, str):
        return obj
    if isinstance(obj, Sequence):
        return [
            dump(value, convert_missing_to_none)
            for value in obj
            if _filter_keep(value, convert_missing_to_none)
        ]
    if isinstance(obj, Mapping):
        return {
            dump(key, convert_missing_to_none): dump(
                value, convert_missing_to_none
            )
            for key, value in obj.items()
            if _filter_keep(value, convert_missing_to_none)
        }
    if convert_missing_to_none and (obj is MISSING):
        return None
    return obj

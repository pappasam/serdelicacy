"""Serialize typed structures into less-typed Python objects."""

from dataclasses import asdict, is_dataclass
from typing import Any, Mapping, Sequence

from .typedefs import UNDEFINED, NamedTupleType


def _filter_keep(value: Any, keep_always: bool) -> bool:
    """Determine whether we should keep a value in serialized output."""
    if keep_always:
        return True
    return value is not UNDEFINED


def dump(obj: Any, convert_undefined_to_none: bool = False) -> Any:
    """Serialize the object into a less-typed form.

    :param convert_undefined_to_none: retain undefined property's key and
        convert its value to None. This will keep all keys when serializing,
        useful if you want to keep all column names and assign value of `None`
        to missing columns.

    Serialize from: - `x` -> `y`:
      - `dataclass` -> `Dict`
      - `NamedTuple` -> `Dict`
      - `str` -> `str`
      - `Sequence` -> `List`
      - `Mapping` -> `Dicts`
      * if `convert_undefined_to_none` is True:
        - `UNDEFINED` -> `None`
      * else
        - `UNDEFINED` keys are filtered out and undefined values are kept as-is
      - `Anything else` -> `itself`
    """
    # pylint: disable=too-many-return-statements
    if is_dataclass(obj):
        return {
            key: dump(value, convert_undefined_to_none)
            for key, value in asdict(obj).items()
            if _filter_keep(value, convert_undefined_to_none)
        }
    if isinstance(obj, NamedTupleType):
        return {
            key: dump(value, convert_undefined_to_none)
            for key, value in obj._asdict().items()
            if _filter_keep(value, convert_undefined_to_none)
        }
    if isinstance(obj, str):
        return obj
    if isinstance(obj, Sequence):
        return [
            dump(value, convert_undefined_to_none)
            for value in obj
            if _filter_keep(value, convert_undefined_to_none)
        ]
    if isinstance(obj, Mapping):
        return {
            dump(key, convert_undefined_to_none): dump(
                value, convert_undefined_to_none
            )
            for key, value in obj.items()
            if _filter_keep(value, convert_undefined_to_none)
        }
    if convert_undefined_to_none and (obj is UNDEFINED):
        return None
    return obj

"""Serdelicacy overrides for dataclasses."""

from dataclasses import dataclass, field
from typing import Any, Callable, NoReturn, TypeVar, Union

T = TypeVar("T")  # pylint: disable=invalid-name


def _noreturn(value: Any) -> NoReturn:  # pylint: disable=unused-argument
    """Simple 1 argument function that returns nothing."""


def _id(value: T) -> T:
    """Identity function."""
    return value


@dataclass(frozen=True)
class Override:
    """Metadata user-defined overrides for dataclass serde.

    :attr dataclass_validate: argument provided only by upstream dataclasses.
        An internal implementation detail, but interesting nonetheless.
        Function either returns `True` on positive validation / `False` on
        non-validation, or returns nothing at all and instead relies on the
        raising of exceptions to indicate whether validation passed for failed.
    :attr dataclass_transform_load: when deserializing, evaluated on an object
        before the object is recursively examined.
    :attr dataclass_transform_postload: when deserializing, evaluated on an
        object after the object has been recursively examined. When possible,
        the `transform_load` should be preferred over `transform_postload`, but
        there are situations where `transform_postload` is useful.
    :attr dataclass_transform_dump: when serializing a dataclass, called on
        value before it is recursively serialized
    """

    validate: Union[
        Callable[[Any], NoReturn],
        Callable[[Any], bool],
        Callable[[Any], None],
    ] = field(default=_noreturn)
    transform_load: Callable[[Any], Any] = field(default=_id)
    transform_postload: Callable[[Any], Any] = field(default=_id)
    transform_dump: Callable[[Any], Any] = field(default=_id)


DEFAULT_OVERRIDE = Override()


def get_override(value: Any) -> Override:
    """Perform validation for override value."""
    if value is None:
        return DEFAULT_OVERRIDE
    if isinstance(value, Override):
        return value
    raise TypeError(
        "dataclasses field error for metadata key 'serdelicacy': value "
        f"{repr(value)} is not the correct type. Expected {repr(Override)}"
    )

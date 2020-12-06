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
    """User-defined overrides for serde with `datacalsses.dataclass`

    Should be passed into the `metadata` argument to `dataclasses.field` via
    the "serdelicacy" key.

    Parameters:
        validate: a function that either returns `True` on positive validation
            / `False` on non-validation, or returns nothing at all and instead
            relies on the raising of exceptions to indicate whether validation
            passed for failed.
        transform_load: a function that, when deserializing, is evaluated on an
            object before the object is recursively examined.
        transform_postload: a function that, when deserializing, is evaluated
            on an object after the object has been recursively examined. When
            possible, the `transform_load` should be preferred over
            `transform_postload`, but there are situations where
            `transform_postload` is useful.
        transform_dump: a function that, when serializing a dataclass, is
            called on its value before it is recursively serialized.

    Example:

        The following example shows how a function, returning `True`/`False`,
        is passed to `serdelicacy.load` through the `metadata` parameter to
        `dataclasses.field`.

        .. code-block:: python

            from dataclasses import dataclass, field
            import serdelicacy
            from serdelicacy import Override

            BOOK_RAW = {"author": "sam"}

            @dataclass
            class Book:
                author: str = field(
                    metadata={"serdelicacy": Override(validate=str.istitle)}
                )

            BOOK = serdelicacy.load(BOOK_RAW, Book)

        This example should raise a `serdelicacy.DeserializeError`
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

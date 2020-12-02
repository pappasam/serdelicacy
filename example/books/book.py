"""An example deserialization of books with validation."""

import json
from dataclasses import dataclass, field
from pprint import pprint
from typing import List, Literal, TypeVar

import serdelicacy
from serdelicacy import OptionalProperty, Override

# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name

T = TypeVar("T")


@dataclass
class Person:
    firstname: str = field(
        metadata={"serdelicacy": Override(validate=str.istitle)}
    )
    lastname: str

    def __post_init__(self):
        # Similar way of validating firstname. Validation error will now take
        # place after the dataclass has been initialized and `lastname` has
        # been deserialized.
        if not self.lastname.istitle():
            raise ValueError("lastname is not propcase")


def _is_title(s: str) -> None:
    """Validate that a string is a title.

    Provide a clear error message!
    """
    if not s.istitle():
        raise ValueError("string is not title case")


@dataclass
class Book:
    isbn: str
    author: Person
    editor: Person
    # note: this validation has a clear error message.
    title: str = field(metadata={"serdelicacy": Override(validate=_is_title)})
    # note: this validation has a horrible error message. Might be worth
    # writing a custom function.
    category: List[str] = field(
        metadata={"serdelicacy": Override(validate=(lambda x: len(x) >= 2))}
    )
    second_author: OptionalProperty[str]
    # transform converts to upper, and dump converts to completely uppercase
    # NOTE: literal type already performs validation
    difficulty: Literal["easy", "medium", "hard"] = field(
        metadata={
            "serdelicacy": Override(
                transform_load=str.lower, transform_dump=str.upper
            )
        }
    )


with open("book.json", "r") as infile:
    raw_data = json.load(infile)


loaded = serdelicacy.load(raw_data, Book)


print("title has been validated:", loaded.title)
print("type of first name:", type(loaded.author.firstname))
print("second author is missing:", loaded.second_author)
print("Difficulty is lowercase:", loaded.difficulty)

unloaded1 = serdelicacy.dump(loaded)

print("Notice how `difficulty` is uppercase? Thanks `dump`!")
pprint(unloaded1)


if not loaded.second_author:
    print("Notice MISSING values are Falsey? I get printed because of this :)")

unloaded2 = serdelicacy.dump(loaded, convert_missing_to_none=True)
print("Notice how `second_author` now exists, with value None?")
pprint(unloaded2)

print("Let's break something to see an error message!")
raw_data["title"] = "I am not title case, so I'll throw an error"
serdelicacy.load(raw_data, Book)

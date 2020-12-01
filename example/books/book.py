"""An example deserialization of books with validation."""

import json
from dataclasses import dataclass, field
from pprint import pprint
from typing import List, Literal, TypeVar

import serdelicacy
from serdelicacy import OptionalProperty

# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name

T = TypeVar("T")


@dataclass
class Person:
    firstname: str = field(metadata={"validate": str.istitle})
    lastname: str

    def __post_init__(self):
        # Similar way of validating firstname. Validation error will now take
        # place after the dataclass has been initialized and `lastname` has
        # been deserialized.
        if not self.lastname.istitle():
            raise ValueError("lastname is not propcase")


def _is_title(s: str) -> None:
    if not s.istitle():
        raise ValueError("string is not title case")


@dataclass
class Book:
    isbn: str
    author: Person
    editor: Person
    # note: this validation has a clear error message.
    title: str = field(metadata={"validate": _is_title})
    # note: this validation has a horrible error message. Might be worth
    # writing a custom function.
    category: List[str] = field(metadata={"validate": (lambda x: len(x) >= 2)})
    second_author: OptionalProperty[str]
    difficulty: Literal["easy", "medium", "hard"]


with open("book.json", "r") as infile:
    raw_data = json.load(infile)


loaded = serdelicacy.load(raw_data, Book)


print(loaded.isbn)
print(loaded.title)
print(type(loaded.author.firstname))
print(loaded.second_author)
print(loaded.difficulty)

unloaded1 = serdelicacy.dump(loaded)
pprint(unloaded1)


if loaded.second_author:
    print("hello")

unloaded2 = serdelicacy.dump(loaded, convert_undefined_to_none=True)
pprint(unloaded2)

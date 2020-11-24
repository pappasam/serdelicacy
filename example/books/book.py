"""An example deserialization of books with validation."""

import json
from dataclasses import dataclass
from pprint import pprint
from typing import List, Literal, TypeVar

import serdelicacy
from serdelicacy import OptionalProperty

# pylint: disable=missing-class-docstring
# pylint: disable=invalid-name

T = TypeVar("T")


@dataclass
class Person:
    firstname: str
    lastname: str

    def __post_init__(self):
        if not self.firstname.istitle():
            raise ValueError("firstname is not propcase")
        if not self.lastname.istitle():
            raise ValueError("lastname is not propcase")


@dataclass
class Book:
    isbn: str
    author: Person
    editor: Person
    title: str
    category: List[str]
    second_author: OptionalProperty[str]
    difficulty: Literal["easy", "medium", "hard"]

    def __post_init__(self) -> None:

        if len(self.category) < 2:
            raise ValueError("Must have at least 2 caregories")


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

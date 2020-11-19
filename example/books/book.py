"""An example deserialization of books with validation."""

import json
from dataclasses import dataclass
from pprint import pprint
from typing import List

import serdataclasses
from serdataclasses import OptionalProperty

# pylint: disable=missing-class-docstring


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
    second_author: OptionalProperty[Person]

    def __post_init__(self) -> None:
        # if self.second_author is UNDEFINED:
        #     self.second_author = Person("John", "Doe")

        if len(self.category) < 2:
            raise ValueError("Must have at least 2 caregories")


with open("book.json", "r") as infile:
    raw_data = json.load(infile)


loaded = serdataclasses.load(raw_data, Book)

print(loaded.isbn)
print(loaded.title)
print(type(loaded.author.firstname))
print(loaded.second_author)

unloaded1 = serdataclasses.dump(loaded)
pprint(unloaded1)

unloaded2 = serdataclasses.dump(loaded, convert_undefined_to_none=True)
pprint(unloaded2)

"""serdataclasses: load and dump data into strongly-typed data structures

This library has two goals:

1. "Deserialize" unstructured Python types into structured, type-hinted Python
    types (dataclasses.dataclass, typing.NamedTuples).
2. "Serialize" structured, type-hinted Python objects into unstructured Python
    types (eg, the reverse).
"""

from .deserialize import DeserializeError, load
from .serialize import dump

"""Goal: load and dump data into strongly-typed data structures.

1. "Deserialize" unstructured Python types into structured, type-hinted Python
   types (dataclasses.dataclass, typing.NamedTuples).
2. "Serialize" structured, type-hinted Python objects into unstructured Python
   types (eg, the reverse).

The top-level module contains `serdelicacy`'s public API and is directly
importable from `serdelicacy`. If you choose to import names from anything
outside of this module, do so at your own risk. Code organization in the
package submodules is subject to change at any time is not reflected in this
library's semantic versioning strategy.
"""

from .deserialize import load
from .errors import DeserializeError, SerdeError, SerializeError
from .overrides import Override
from .serialize import dump
from .typedefs import OptionalProperty, get, is_missing

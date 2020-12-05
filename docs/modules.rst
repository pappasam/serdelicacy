##########
Public API
##########

.. automodule:: serdelicacy

This section documents `serdelicacy`'s public API. `serdelicacy`'s public API is directly importable from `serdelicacy`. If you choose to import names from anything outside of `serdelicacy`'s top-level module, do so at your own risk. Code organization is subject to change at any time is not reflected in this library's semantic versioning strategy.

Deserialize
===========

.. autofunction:: serdelicacy.load

.. autofunction:: serdelicacy.get

.. autofunction:: serdelicacy.is_missing

.. autoexception:: serdelicacy.DeserializeError
    :show-inheritance:

Serialize
=========

.. autofunction:: serdelicacy.dump

.. autoexception:: serdelicacy.SerializeError
    :show-inheritance:

Both Serialize and Deserialize
==============================

.. autodata:: serdelicacy.OptionalProperty

   **Example**

   .. code-block:: python

       from typing import List, Optional
       from dataclasses import dataclass
       import serdelicacy
       from serdelicacy import OptionalProperty

       DATA = [
           {
               "hello": "friend",
               "world": "foe",
           },
           {
               "hello": "Rawr",
           },
           {
               "hello": None,
               "world": "hehe",
           },
       ]

       @dataclass
       class HelloWorld:
           hello: Optional[str]
           world: OptionalProperty[str]

       PARSED = serdelicacy.load(DATA, List[HelloWorld])

       assert serdelicacy.is_missing(PARSED[1].world)
       assert not PARSED[1].world  # note: it's Falsey!
       assert PARSED[2].hello is None

.. autoclass:: serdelicacy.Override

.. autoexception:: serdelicacy.SerdeError
    :show-inheritance:

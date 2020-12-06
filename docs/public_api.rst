##########
Public API
##########

.. automodule:: serdelicacy

Deserialization
===============

This function is the entrypoint to `serdelicacy`'s deserialization process:

.. autofunction:: serdelicacy.load

Serialization
=============

This function is the entrypoint to `serdelicacy`'s serialization process:

.. autofunction:: serdelicacy.dump

Utilities
=========

You may use the following tools to:

1. Operate on `serdelicacy`-affecred Python values in a typesafe way
2. Augment `dataclasses.dataclass` to give `serdelicacy` more information about how to process data.

.. autofunction:: serdelicacy.get

.. autofunction:: serdelicacy.is_missing

.. autoclass:: serdelicacy.Override

Types
=====

The following types are custom to `serdelicacy`:

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

Exceptions
==========

`serdelicacy` may raise the following Python exceptions during the serialization and/or the deserialization process.

.. autoexception:: serdelicacy.SerdeError
    :show-inheritance:

.. autoexception:: serdelicacy.DeserializeError
    :show-inheritance:

.. autoexception:: serdelicacy.SerializeError
    :show-inheritance:

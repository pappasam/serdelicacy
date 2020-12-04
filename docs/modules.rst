##########
Public API
##########

.. automodule:: serdelicacy

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

.. autoclass:: serdelicacy.Override

.. autoexception:: serdelicacy.SerdeError
    :show-inheritance:

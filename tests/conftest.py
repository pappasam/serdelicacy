"""Pytest configuration file, fixtures shared across all tests"""

from dataclasses import dataclass
from typing import List, Union, Optional

import pytest



# @pytest.fixture
# def data_big():
#     """Obtain the test value"""
#     return {
#         "x": 12,
#         "y": "hello",
#         "z": 12.41,
#         "l": [{"y": [1, 2, 3]}, {"y": [4, 5, 6]}],
#         "p": ["hello", "world", {"y": [1, 2, 3]}, {"y": [4, 5, 6]}],
#         "b": [tuple(), tuple(), tuple()],
#     }

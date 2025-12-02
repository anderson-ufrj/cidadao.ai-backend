"""
Fast JSON serialization/deserialization utilities using orjson.

This module provides drop-in replacements for standard json functions
with significant performance improvements.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID

import orjson
from pydantic import BaseModel


def default(obj: Any) -> Any:
    """
    Custom serializer for orjson to handle special types.
    """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    if isinstance(obj, UUID):
        return str(obj)
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, BaseModel):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return obj.__dict__
    raise TypeError(f"Type {type(obj)} not serializable")


def dumps(obj: Any, *, indent: bool = False) -> str:
    """
    Serialize obj to a JSON formatted string using orjson.

    Args:
        obj: Object to serialize
        indent: Whether to indent the output (slower but prettier)

    Returns:
        JSON string
    """
    options = orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
    if indent:
        options |= orjson.OPT_INDENT_2

    return orjson.dumps(obj, default=default, option=options).decode("utf-8")


def loads(s: str | bytes) -> Any:
    """
    Deserialize s (a str or bytes containing JSON) to a Python object.

    Args:
        s: JSON string or bytes to deserialize

    Returns:
        Python object
    """
    if isinstance(s, str):
        s = s.encode("utf-8")
    return orjson.loads(s)


def dumps_bytes(obj: Any, *, indent: bool = False) -> bytes:
    """
    Serialize obj to JSON bytes (faster than dumps when you need bytes).

    Args:
        obj: Object to serialize
        indent: Whether to indent the output

    Returns:
        JSON bytes
    """
    options = orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
    if indent:
        options |= orjson.OPT_INDENT_2

    return orjson.dumps(obj, default=default, option=options)


# FastAPI response helper
def jsonable_encoder(
    obj: Any, *, exclude_unset: bool = False, exclude_none: bool = False
) -> Any:
    """
    Convert a Python object to a JSON-compatible format.

    Args:
        obj: Object to convert
        exclude_unset: Exclude unset fields from Pydantic models
        exclude_none: Exclude None values

    Returns:
        JSON-compatible Python object
    """
    if isinstance(obj, BaseModel):
        return obj.model_dump(exclude_unset=exclude_unset, exclude_none=exclude_none)

    # For other objects, serialize and deserialize to ensure compatibility
    return loads(dumps(obj))


# Aliases for drop-in replacement
encode = dumps
decode = loads

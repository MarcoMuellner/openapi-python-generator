import keyword
import re
from typing import Optional
from openapi_python_generator.common import PydanticVersion


_use_orjson: bool = False
_pydantic_version: PydanticVersion = PydanticVersion.V2
_custom_template_path: str = None
_pydantic_use_awaredatetime: bool = False
_symbol_ascii_strip_re = re.compile(r"[^A-Za-z0-9_]")


def set_use_orjson(value: bool) -> None:
    """
    Set the value of the global variable _use_orjson.
    :param value: value of the variable
    """
    global _use_orjson
    _use_orjson = value

def set_pydantic_version(value: PydanticVersion) -> None:
    """
    Set the value of the global variable
    :param value: value of the variable
    """
    global _pydantic_version
    _pydantic_version = value

def get_use_orjson() -> bool:
    """
    Get the value of the global variable _use_orjson.
    :return: value of the variable
    """
    global _use_orjson
    return _use_orjson

def get_pydantic_version() -> PydanticVersion:
    """
    Get the value of the global variable _pydantic_version.
    :return: value of the variable
    """
    global _pydantic_version
    return _pydantic_version

def set_custom_template_path(value: Optional[str]) -> None:
    """
    Set the value of the global variable _custom_template_path.
    :param value: value of the variable
    """
    global _custom_template_path
    _custom_template_path = value


def get_custom_template_path() -> Optional[str]:
    """
    Get the value of the global variable _custom_template_path.
    :return: value of the variable
    """
    global _custom_template_path
    return _custom_template_path


def set_pydantic_use_awaredatetime(value: bool) -> None:
    """
    Set whether to use AwareDateTime from pydantic instead of datetime.
    :param value: value of the variable
    """
    global _pydantic_use_awaredatetime
    _pydantic_use_awaredatetime = value

def get_pydantic_use_awaredatetime() -> bool:
    """
    Get whether to use AwareDateTime from pydantic instead of datetime.
    :return: value of the variable
    """
    global _pydantic_use_awaredatetime
    return _pydantic_use_awaredatetime


def normalize_symbol(symbol: str) -> str:
    """
    Remove invalid characters & keywords in Python symbol names
    :param symbol: name of the identifier
    :return: normalized identifier name
    """
    symbol = symbol.replace("-", "_")
    normalized_symbol = _symbol_ascii_strip_re.sub("", symbol)
    if normalized_symbol in keyword.kwlist:
        normalized_symbol = normalized_symbol + "_"
    return normalized_symbol

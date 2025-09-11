import keyword
import re
from typing import Optional

_use_orjson: bool = False
_custom_template_path: Optional[str] = None
_symbol_ascii_strip_re = re.compile(r"[^A-Za-z0-9_]")


def set_use_orjson(value: bool) -> None:
    """
    Set the value of the global variable _use_orjson.
    :param value: value of the variable
    """
    global _use_orjson
    _use_orjson = value


def get_use_orjson() -> bool:
    """
    Get the value of the global variable _use_orjson.
    :return: value of the variable
    """
    global _use_orjson
    return _use_orjson


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


def normalize_symbol(symbol: str) -> str:
    """
    Remove invalid characters & keywords in Python symbol names
    :param symbol: name of the identifier
    :return: normalized identifier name
    """
    symbol = symbol.replace("-", "_").replace(" ", "_")
    normalized_symbol = _symbol_ascii_strip_re.sub("", symbol)
    if normalized_symbol in keyword.kwlist:
        normalized_symbol = normalized_symbol + "_"
    if len(normalized_symbol) > 0 and normalized_symbol[0].isnumeric():
        normalized_symbol = "_" + normalized_symbol
    return normalized_symbol

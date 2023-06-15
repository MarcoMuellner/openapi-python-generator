import keyword
import re
from typing import List


_use_orjson: bool = False
_dict_args: List[str] = []
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


def set_dict_args(value: List[str]):
    """
    Set the value of the global variable _dict_args.
    :param value: value of the variable
    """
    global _dict_args
    _dict_args = value


def get_dict_args() -> List[str]:
    """
    Get the value of the global variable _dict_args.
    :return: value of the variable
    """
    global _dict_args
    return _dict_args


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

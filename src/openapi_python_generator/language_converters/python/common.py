_use_orjson: bool = False


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

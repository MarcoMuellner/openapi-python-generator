from enum import Enum

from openapi_python_generator.models import LibraryConfig


class HTTPLibrary(str, Enum):
    """
    Enum for the available HTTP libraries.
    """

    httpx = "httpx"
    requests = "requests"
    aiohttp = "aiohttp"


library_config_dict = {
    HTTPLibrary.httpx: LibraryConfig(
        name="httpx", library_name="httpx", include_async=True, include_sync=True
    ),
    HTTPLibrary.requests: LibraryConfig(
        name="requests", library_name="requests", include_async=False, include_sync=True
    ),
    HTTPLibrary.aiohttp: LibraryConfig(
        name="aiohttp", library_name="aiohttp", include_async=True, include_sync=False
    ),
}

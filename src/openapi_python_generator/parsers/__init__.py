"""
OpenAPI parsers for different specification versions.
"""

from .openapi_30 import parse_openapi_30, generate_code_30
from .openapi_31 import parse_openapi_31, generate_code_31

__all__ = [
    "parse_openapi_30",
    "generate_code_30",
    "parse_openapi_31",
    "generate_code_31",
]

"""
OpenAPI 3.1 specific parsing and generation.
"""

from typing import Optional

from openapi_pydantic.v3.v3_1 import OpenAPI

from openapi_python_generator.common import HTTPLibrary, PydanticVersion
from openapi_python_generator.language_converters.python.generator import (
    generator as base_generator,
)
from openapi_python_generator.models import ConversionResult


def parse_openapi_3_1(spec_data: dict) -> OpenAPI:
    """
    Parse OpenAPI 3.1 specification data.

    Args:
        spec_data: Dictionary containing OpenAPI 3.1 specification

    Returns:
        OpenAPI: Parsed OpenAPI 3.1 specification object

    Raises:
        ValidationError: If the specification is invalid
    """
    return OpenAPI(**spec_data)  # type: ignore - pydantic issue with extra fields


def generate_code_3_1(
    data: OpenAPI,
    library: HTTPLibrary = HTTPLibrary.httpx,
    env_token_name: Optional[str] = None,
    use_orjson: bool = False,
    custom_template_path: Optional[str] = None,
    pydantic_version: PydanticVersion = PydanticVersion.V2,
) -> ConversionResult:
    """
    Generate Python code from OpenAPI 3.1 specification.

    Args:
        data: OpenAPI 3.1 specification object
        library: HTTP library to use
        env_token_name: Environment variable name for token
        use_orjson: Whether to use orjson for serialization
        custom_template_path: Custom template path
        pydantic_version: Pydantic version to use

    Returns:
        ConversionResult: Generated code and metadata
    """
    from openapi_python_generator.common import library_config_dict

    library_config = library_config_dict[library]

    return base_generator(
        data=data,
        library_config=library_config,
        env_token_name=env_token_name,
        use_orjson=use_orjson,
        custom_template_path=custom_template_path,
        pydantic_version=pydantic_version,
    )

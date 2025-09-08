"""
OpenAPI version detection utilities.
"""

from typing import Any, Dict, Literal

OpenAPIVersion = Literal["3.0", "3.1"]


def detect_openapi_version(spec_data: Dict[str, Any]) -> OpenAPIVersion:
    """
    Detect the OpenAPI version from specification data.

    Performs basic validation to ensure the specification is well-formed enough
    to route to the appropriate parser. The actual parser will handle detailed
    validation of the specification content.

    Args:
        spec_data: Dictionary containing OpenAPI specification

    Returns:
        OpenAPIVersion: Either "3.0" or "3.1"

    Raises:
        ValueError: If the specification is malformed or has unsupported version
    """
    # Basic validation: must be a dictionary
    if not isinstance(spec_data, dict):
        raise ValueError("OpenAPI specification must be a dictionary/object")

    # Basic validation: must have openapi field
    if "openapi" not in spec_data:
        raise ValueError("Missing required 'openapi' field in specification")

    openapi_version = spec_data.get("openapi")

    # Basic validation: openapi field must be a string
    if not isinstance(openapi_version, str):
        raise ValueError("'openapi' field must be a string")

    # Basic validation: must not be empty
    if not openapi_version.strip():
        raise ValueError("'openapi' field cannot be empty")

    # Version detection
    if openapi_version.startswith("3.0"):
        return "3.0"
    elif openapi_version.startswith("3.1"):
        return "3.1"
    else:
        raise ValueError(
            f"Unsupported OpenAPI version: {openapi_version}. "
            f"Only OpenAPI 3.0.x and 3.1.x are supported."
        )


def is_openapi_30(spec_data: Dict[str, Any]) -> bool:
    """Check if the specification is OpenAPI 3.0.x"""
    try:
        return detect_openapi_version(spec_data) == "3.0"
    except ValueError:
        return False


def is_openapi_31(spec_data: Dict[str, Any]) -> bool:
    """Check if the specification is OpenAPI 3.1.x"""
    try:
        return detect_openapi_version(spec_data) == "3.1"
    except ValueError:
        return False

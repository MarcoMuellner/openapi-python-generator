from typing import Optional

from openapi_schema_pydantic import OpenAPI

from openapi_python_generator.language_converters.python import common
from openapi_python_generator.language_converters.python.api_config_generator import (
    generate_api_config,
)
from openapi_python_generator.language_converters.python.model_generator import (
    generate_models,
)
from openapi_python_generator.language_converters.python.service_generator import (
    generate_services,
)
from openapi_python_generator.models import ConversionResult
from openapi_python_generator.models import LibraryConfig


def generator(
    data: OpenAPI,
    library_config: LibraryConfig,
    env_token_name: Optional[str] = None,
    use_orjson: bool = False,
) -> ConversionResult:
    """
    Generate Python code from an OpenAPI 3.0 specification.
    """

    common.set_use_orjson(use_orjson)

    if data.components is not None:
        models = generate_models(data.components)
    else:
        models = []

    if data.paths is not None:
        services = generate_services(data.paths, library_config)
    else:
        services = []

    api_config = generate_api_config(data, env_token_name)

    return ConversionResult(
        models=models,
        services=services,
        api_config=api_config,
    )

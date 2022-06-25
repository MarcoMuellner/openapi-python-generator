from openapi_schema_pydantic import OpenAPI

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


def generator(data: OpenAPI) -> ConversionResult:
    """
    Generate Python code from an OpenAPI 3.0 specification.
    """

    models = generate_models(data.components)
    services = generate_services(data.paths)
    api_config = generate_api_config(data)

    return ConversionResult(
        models=models,
        services=services,
        api_config=api_config,
    )

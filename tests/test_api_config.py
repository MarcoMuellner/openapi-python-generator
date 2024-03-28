from openapi_pydantic import OpenAPI

from openapi_python_generator.language_converters.python.api_config_generator import (
    generate_api_config,
)


def test_generate_api_config(model_data: OpenAPI):
    api_config = generate_api_config(model_data)
    assert api_config.file_name == "api_config"

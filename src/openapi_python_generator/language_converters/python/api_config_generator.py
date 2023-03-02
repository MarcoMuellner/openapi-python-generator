from typing import Optional

from openapi_schema_pydantic import OpenAPI

from openapi_python_generator.language_converters.python.jinja_config import (
    API_CONFIG_TEMPLATE,
)
from openapi_python_generator.language_converters.python.jinja_config import JINJA_ENV
from openapi_python_generator.models import APIConfig


def generate_api_config(
    data: OpenAPI, env_token_name: Optional[str] = None
) -> APIConfig:
    """
    Generate the API model.
    """
    return APIConfig(
        file_name="api_config",
        content=JINJA_ENV.get_template(API_CONFIG_TEMPLATE).render(
            env_token_name=env_token_name, **data.dict()
        ),
        base_url=data.servers[0].url if len(data.servers) > 0 else "NO SERVER",
    )

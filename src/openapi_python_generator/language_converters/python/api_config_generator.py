from typing import Optional

from openapi_pydantic.v3 import OpenAPI

from openapi_python_generator.common import PydanticVersion
from openapi_python_generator.language_converters.python.jinja_config import (
    API_CONFIG_TEMPLATE,
    API_CONFIG_TEMPLATE_PYDANTIC_V2,
    create_jinja_env,
)
from openapi_python_generator.models import APIConfig


def generate_api_config(
    data: OpenAPI,
    env_token_name: Optional[str] = None,
    pydantic_version: PydanticVersion = PydanticVersion.V2,
) -> APIConfig:
    """
    Generate the API model.
    """

    template_name = (
        API_CONFIG_TEMPLATE_PYDANTIC_V2
        if pydantic_version == PydanticVersion.V2
        else API_CONFIG_TEMPLATE
    )
    jinja_env = create_jinja_env()
    return APIConfig(
        file_name="api_config",
        content=jinja_env.get_template(template_name).render(
            env_token_name=env_token_name, **data.model_dump()
        ),
        base_url=data.servers[0].url if len(data.servers) > 0 else "NO SERVER",
    )

from pathlib import Path

from jinja2 import ChoiceLoader, Environment, FileSystemLoader

from . import common

ENUM_TEMPLATE = "enum.jinja2"
MODELS_TEMPLATE = "models.jinja2"
MODELS_TEMPLATE_PYDANTIC_V2 = "models_pydantic_2.jinja2"
SERVICE_TEMPLATE = "service.jinja2"
HTTPX_TEMPLATE = "httpx.jinja2"
API_CONFIG_TEMPLATE = "apiconfig.jinja2"
API_CONFIG_TEMPLATE_PYDANTIC_V2 = "apiconfig_pydantic_2.jinja2"
TEMPLATE_PATH = Path(__file__).parent / "templates"


def create_jinja_env():
    custom_template_path = common.get_custom_template_path()
    environment = Environment(
        loader=(
            ChoiceLoader(
                [
                    FileSystemLoader(custom_template_path),
                    FileSystemLoader(TEMPLATE_PATH),
                ]
            )
            if custom_template_path is not None
            else FileSystemLoader(TEMPLATE_PATH)
        ),
        autoescape=True,
        trim_blocks=True,
    )

    environment.filters["normalize_symbol"] = common.normalize_symbol

    return environment

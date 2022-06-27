from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ENUM_TEMPLATE = "enum.template"
MODELS_TEMPLATE = "models.template"
SERVICE_TEMPLATE = "service.template"
HTTPX_TEMPLATE = "httpx.template"
API_CONFIG_TEMPLATE = "apiconfig.template"
TEMPLATE_PATH = Path(__file__).parent / "templates"

JINJA_ENV = Environment(
    loader=FileSystemLoader(TEMPLATE_PATH), autoescape=True, trim_blocks=True
)

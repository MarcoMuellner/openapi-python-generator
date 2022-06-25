from pathlib import Path

from jinja2 import Environment, FileSystemLoader

ENUM_TEMPLATE = "enum.template"
MODELS_TEMPLATE = "models.template"
SERVICE_TEMPLATE = "service.template"
HTTPX_TEMPLATE = "httpx.template"
API_CONFIG_TEMPLATE = "apiconfig.template"
_template_path = Path(__file__).parent / "templates"

JINJA_ENV = Environment(
    loader=FileSystemLoader(_template_path), autoescape=True, trim_blocks=True
)

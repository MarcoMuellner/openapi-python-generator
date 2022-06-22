from pathlib import Path

from jinja2 import Environment, FileSystemLoader

MODELS_TEMPLATE = "models.template"
SERVICE_TEMPLATE = "services.template"
HTTPX_TEMPLATE = "httpx.template"
_template_path = Path(__file__).parent / "templates"

JINJA_ENV = Environment(loader=FileSystemLoader(_template_path), autoescape=True, trim_blocks=True)

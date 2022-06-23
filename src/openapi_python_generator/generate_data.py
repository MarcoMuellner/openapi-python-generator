from pathlib import Path
from typing import Optional

import httpx
from httpx import ConnectError
from orjson import orjson
import typer
from pydantic import ValidationError

from common import HTTPLibrary
from openapi_schema_pydantic import OpenAPI
from language_converters.python.generator import generator
from src.openapi_python_generator.language_converters.python.jinja_config import JINJA_ENV, SERVICE_TEMPLATE
from src.openapi_python_generator.models import ConversionResult


def get_open_api(path: str) -> OpenAPI:
    """
    Tries to fetch the openapi.json file from the web or load from a local file. Returns the according OpenAPI object.
    :param path:
    :return:
    """
    try:
        if path.startswith("http://") or path.startswith("https://"):
            return OpenAPI(**orjson.loads(httpx.get(path).text))

        with open(path, 'r') as f:
            return OpenAPI(**orjson.loads(f.read()))
    except FileNotFoundError:
        typer.echo(f"File {path} not found. Please make sure to pass the path to the OpenAPI 3.0 specification.")
        typer.Exit(1)
    except ConnectError:
        typer.echo(f"Could not connect to {path}.")
        typer.Exit(1)
    except ValidationError:
        typer.echo(f"File {path} is not a valid OpenAPI 3.0 specification, or there may be a problem with your JSON.")
        typer.Exit(1)


def write_data(data: ConversionResult, output: str):
    """
    This function will firstly create the folderstrucutre of output, if it doesn't exist. Then it will create the
    models from data.models into the models sub module of the output folder. After this, the services will be created
    into the services sub module of the output folder.
    :param data: The data to write.
    :param output: The path to the output folder.
    """

    # Create the folder structure of the output folder.
    Path(output).mkdir(parents=True, exist_ok=True)

    # Create the models module.
    models_path = Path(output) / "models"
    models_path.mkdir(parents=True, exist_ok=True)

    # Create the services module.
    services_path = Path(output) / "services"
    services_path.mkdir(parents=True, exist_ok=True)

    files = []

    # Write the models.
    for model in data.models:
        files.append(model.file_name)
        with open(models_path / f"{model.file_name}.py", 'w') as f:
            f.write(model.content)

    # Create models.__init__.py file containing imports to all models.

    with open(models_path / "__init__.py", 'w') as f:
        f.write("\n".join([f'from {file} import *' for file in files]))

    files = []

    # Write the services.
    for service in data.services:
        files.append(service.file_name)
        with open(services_path / f"{service.file_name}.py", 'w') as f:
            f.write(JINJA_ENV.get_template(SERVICE_TEMPLATE).render(**service.dict()))

    # Create services.__init__.py file containing imports to all services.
    with open(services_path / "__init__.py", 'w') as f:
        f.write("\n".join([f'from {file} import *' for file in files]))

    # Write the api_config.py file.
    with open(Path(output) / "api_config.py", 'w') as f:
        f.write(data.api_config.content)

    #Write the __init__.py file.
    with open(Path(output) / "__init__.py", 'w') as f:
        f.write("from models import *")
        f.write("from services import *")
        f.write("from api_config import *")


def generate_data(file_name: str, output: str, library: Optional[HTTPLibrary] = HTTPLibrary.httpx) -> None:
    """
    Generate Python code from an OpenAPI 3.0 specification.
    """
    data = get_open_api(file_name)
    typer.echo(f"Generating data from {file_name}")
    result = generator(data)
    write_data(result, output)

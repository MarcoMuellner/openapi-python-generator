from pathlib import Path
from typing import Optional
from typing import Union

import black
import click
import httpx
import isort
import orjson
from black import NothingChanged
from httpx import ConnectError
from httpx import ConnectTimeout
from openapi_schema_pydantic import OpenAPI
from pydantic import ValidationError

from .common import HTTPLibrary
from .common import library_config_dict
from .language_converters.python.generator import generator
from .language_converters.python.jinja_config import JINJA_ENV
from .language_converters.python.jinja_config import SERVICE_TEMPLATE
from .models import ConversionResult


def write_code(path: Path, content) -> None:
    """
    Write the content to the file at the given path.
    :param autoformat: The autoformat applied to the code written.
    :param path: The path to the file.
    :param content: The content to write.
    """
    try:
        with open(path, "w") as f:
            try:
                formatted_contend = black.format_file_contents(
                    content, fast=False, mode=black.FileMode(line_length=120)
                )

            except NothingChanged:
                formatted_contend = content
            formatted_contend = isort.code(formatted_contend, line_length=120)
            f.write(formatted_contend)
    except Exception as e:
        raise e


def get_open_api(source: Union[str, Path]) -> OpenAPI:
    """
    Tries to fetch the openapi.json file from the web or load from a local file. Returns the according OpenAPI object.
    :param source:
    :return:
    """
    try:
        if not isinstance(source, Path) and (
            source.startswith("http://") or source.startswith("https://")
        ):
            return OpenAPI(**orjson.loads(httpx.get(source).text))

        with open(source, "r") as f:
            return OpenAPI(**orjson.loads(f.read()))
    except FileNotFoundError:
        click.echo(
            f"File {source} not found. Please make sure to pass the path to the OpenAPI 3.0 specification."
        )
        raise
    except (ConnectError, ConnectTimeout):
        click.echo(f"Could not connect to {source}.")
        raise ConnectError(f"Could not connect to {source}.") from None
    except (ValidationError, orjson.JSONDecodeError):
        click.echo(
            f"File {source} is not a valid OpenAPI 3.0 specification, or there may be a problem with your JSON."
        )
        raise


def write_data(data: ConversionResult, output: Union[str, Path]) -> None:
    """
    This function will firstly create the folderstrucutre of output, if it doesn't exist. Then it will create the
    models from data.models into the models sub module of the output folder. After this, the services will be created
    into the services sub module of the output folder.
    :param autoformat: The autoformat applied to the code written.
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
        write_code(models_path / f"{model.file_name}.py", model.content)

    # Create models.__init__.py file containing imports to all models.
    write_code(
        models_path / "__init__.py",
        "\n".join([f"from .{file} import *" for file in files]),
    )

    files = []

    # Write the services.
    for service in data.services:
        if len(service.operations) == 0:
            continue
        files.append(service.file_name)
        write_code(
            services_path / f"{service.file_name}.py",
            JINJA_ENV.get_template(SERVICE_TEMPLATE).render(**service.dict()),
        )

    # Create services.__init__.py file containing imports to all services.
    write_code(services_path / "__init__.py", "")

    # Write the api_config.py file.
    write_code(Path(output) / "api_config.py", data.api_config.content)

    # Write the __init__.py file.
    write_code(
        Path(output) / "__init__.py",
        "from .models import *\nfrom .services import *\nfrom .api_config import *",
    )


def generate_data(
    source: Union[str, Path],
    output: Union[str, Path],
    library: Optional[HTTPLibrary] = HTTPLibrary.httpx,
    env_token_name: Optional[str] = None,
    use_orjson: bool = False,
) -> None:
    """
    Generate Python code from an OpenAPI 3.0 specification.
    """
    data = get_open_api(source)
    click.echo(f"Generating data from {source}")

    result = generator(data, library_config_dict[library], env_token_name, use_orjson)

    write_data(result, output)

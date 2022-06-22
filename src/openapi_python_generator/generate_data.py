from typing import Optional

import httpx
from orjson import orjson
import typer
from pydantic import ValidationError

from common import HTTPLibrary
from openapi_schema_pydantic import OpenAPI
from language_converters.python.generator import generator


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
        typer.Exit()
    except ValidationError:
        typer.echo(f"File {path} is not a valid OpenAPI 3.0 specification, or there may be a problem with your JSON.")
        typer.Exit()


def generate_data(file_name: str, output: str, library: Optional[HTTPLibrary] = HTTPLibrary.httpx) -> None:
    """
    Generate Python code from an OpenAPI 3.0 specification.
    """
    data = get_open_api(file_name)
    typer.echo(f"Generating data from {file_name}")
    result = generator(data)


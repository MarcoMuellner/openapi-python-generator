from typing import Optional

import click

from openapi_python_generator import __version__
from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.generate_data import generate_data


@click.command()
@click.argument("source")
@click.argument("output")
@click.option(
    "--library",
    default=HTTPLibrary.httpx,
    type=HTTPLibrary,
    show_default=True,
    help="HTTP library to use in the generation of the client.",
)
@click.option(
    "--env-token-name",
    default="access_token",
    show_default=True,
    help="Name of the environment variable that contains the token. If you set this, the code expects this environment "
    "variable to be set and will raise an error if it is not.",
)
@click.option(
    "--use-orjson",
    is_flag=True,
    show_default=True,
    default=False,
    help="Use the orjson library to serialize the data. This is faster than the default json library and provides "
    "serialization of datetimes and other types that are not supported by the default json library.",
)
@click.version_option(version=__version__)
def main(
    source: str,
    output: str,
    library: Optional[HTTPLibrary] = HTTPLibrary.httpx,
    env_token_name: Optional[str] = None,
    use_orjson: bool = False,
) -> None:
    """
    Generate Python code from an OpenAPI 3.0 specification.

    Provide a SOURCE (file or URL) containing the OpenAPI 3 specification and
    an OUTPUT path, where the resulting client is created.
    """
    generate_data(source, output, library, env_token_name, use_orjson)


if __name__ == "__main__":  # pragma: no cover
    main()

from typing import Optional

import typer

from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.generate_data import generate_data

app = typer.Typer()


@app.command()
def main(file_name :str, output : str, library : Optional[HTTPLibrary]  = HTTPLibrary.httpx) -> None:
    """
    Generate Python code from an OpenAPI 3.0 specification.
    """
    generate_data(file_name, output, library)



if __name__ == "__main__": #pragma: no cover
    app()


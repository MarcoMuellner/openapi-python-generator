import pytest
from click.testing import CliRunner
from openapi_schema_pydantic import OpenAPI

from openapi_python_generator.__main__ import main
from openapi_python_generator.common import HTTPLibrary, library_config_dict
from openapi_python_generator.exceptions import InvalidDataclassError
from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.language_converters.python.generator import generator
from tests.conftest import test_data_folder
from tests.conftest import test_result_path


@pytest.mark.parametrize(
    "library",
    [HTTPLibrary.httpx, HTTPLibrary.aiohttp, HTTPLibrary.requests],
)
def test_issue_11(library) -> None:
    """
    https://github.com/MarcoMuellner/openapi-python-generator/issues/31
    """
    data = {"openapi": "3.0.1", "info": {"title": "searchword", "description": "", "version": "1.0.0"}, "tags": [],
            "paths": {"/apipath/login": {
                "post": {"summary": "login接口", "x-apifox-folder": "", "x-apifox-status": "developing",
                         "deprecated": False, "description": "", "tags": [], "parameters": [
                        {"name": "username", "in": "query", "description": "", "required": True,
                         "example": "{{username}}", "schema": {"type": "string"}},
                        {"name": "passwd", "in": "query", "description": "", "required": True, "example": "{{passwd}}",
                         "schema": {"type": "string"}}]}}}}

    openapi_conversion = OpenAPI(**data)
    with pytest.raises(InvalidDataclassError):
        generator(openapi_conversion, library_config_dict[library], None, False)



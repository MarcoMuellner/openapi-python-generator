import pytest

from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.generate_data import get_open_api
from openapi_python_generator.parsers import generate_code_3_1
from tests.conftest import test_data_folder


@pytest.mark.parametrize(
    "library",
    [HTTPLibrary.httpx, HTTPLibrary.aiohttp, HTTPLibrary.requests],
)
def test_issue_30_87(library) -> None:
    """
    https://github.com/MarcoMuellner/openapi-python-generator/issues/30
    https://github.com/MarcoMuellner/openapi-python-generator/issues/87
    """
    openapi_obj, version = get_open_api(str(test_data_folder / "issue_30_87.json"))
    result = generate_code_3_1(openapi_obj, library)  # type: ignore

    expected_model = [m for m in result.models if m.openapi_object.title == "UserType"][
        0
    ]
    assert "ADMIN_USER = 'admin-user'" in expected_model.content

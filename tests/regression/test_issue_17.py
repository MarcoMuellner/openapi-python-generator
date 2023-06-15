import pytest
from click.testing import CliRunner

from openapi_python_generator.__main__ import main
from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.generate_data import generate_data
from tests.conftest import test_data_folder
from tests.conftest import test_result_path


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.mark.parametrize(
    "library",
    [HTTPLibrary.httpx, HTTPLibrary.aiohttp, HTTPLibrary.requests],
)
def test_issue_11(runner: CliRunner, model_data_with_cleanup, library) -> None:
    """
    https://github.com/MarcoMuellner/openapi-python-generator/issues/7
    """
    assert (generate_data(test_data_folder / "issue_17.json",
                  test_result_path,
                  ["exclude_unset=True"],
                  library) is None
)

"""Test cases for the __main__ module."""
import pytest
from click.testing import CliRunner

from openapi_python_generator.__main__ import main
from openapi_python_generator.common import HTTPLibrary
from tests.conftest import test_data_path
from tests.conftest import test_result_path


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.mark.parametrize(
    "library",
    [HTTPLibrary.httpx, HTTPLibrary.requests, HTTPLibrary.aiohttp],
)
def test_main_succeeds(runner: CliRunner, model_data_with_cleanup, library) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        main,
        [str(test_data_path), str(test_result_path), "--library", library.value],
    )
    assert result.exit_code == 0

"""Test cases for the __main__ module."""
import pytest
from click.testing import CliRunner

from openapi_python_generator.__main__ import main
from openapi_python_generator.common import HTTPLibrary, AutoFormat
from tests.conftest import test_data_path, test_result_path


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.mark.parametrize(
    "library,autoformat",
    [
        (HTTPLibrary.httpx, AutoFormat.black),
        (HTTPLibrary.httpx, AutoFormat.autopep8),
        (HTTPLibrary.httpx, AutoFormat.none),
        (HTTPLibrary.requests, AutoFormat.black),
        (HTTPLibrary.requests, AutoFormat.autopep8),
        (HTTPLibrary.requests, AutoFormat.none),
    ],
)
def test_main_succeeds(
    runner: CliRunner, model_data_with_cleanup, library, autoformat
) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(
        main,
        [
            str(test_data_path),
            str(test_result_path),
            "--library",
            library.value,
            "--autoformat",
            autoformat.value,
        ],
    )
    assert result.exit_code == 0

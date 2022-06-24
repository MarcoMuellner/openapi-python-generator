"""Test cases for the __main__ module."""
import pytest
from typer.testing import CliRunner

from openapi_python_generator import __main__
from openapi_python_generator.__main__ import app


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner, model_data_with_cleanup) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(app, ["test_data/test_api.json", "test_result"])


"""Test cases for the __main__ module."""
import pytest
from click.testing import CliRunner

from openapi_python_generator.__main__ import main
from tests.conftest import test_data_path, test_result_path


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


def test_main_succeeds(runner: CliRunner, model_data_with_cleanup) -> None:
    """It exits with a status code of zero."""
    result = runner.invoke(main, [str(test_data_path), str(test_result_path)])
    assert result.exit_code == 0

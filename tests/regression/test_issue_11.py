import pytest
from click.testing import CliRunner

from openapi_python_generator.__main__ import main
from openapi_python_generator.common import HTTPLibrary
from tests.conftest import test_data_folder
from tests.conftest import test_result_path


@pytest.fixture
def runner() -> CliRunner:
    """Fixture for invoking command-line interfaces."""
    return CliRunner()


@pytest.mark.parametrize(
    "library",
    [HTTPLibrary.httpx, HTTPLibrary.requests, HTTPLibrary.aiohttp],
)
def test_issue_11(runner: CliRunner, model_data_with_cleanup, library) -> None:
    """
    https://github.com/MarcoMuellner/openapi-python-generator/issues/7
    """
    result = runner.invoke(
        main,
        [
            str(test_data_folder / "openapi_gitea_converted.json"),
            str(test_result_path),
            "--library",
            library.value,
        ],
    )
    assert result.exit_code == 0

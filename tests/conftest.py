import json
import shutil
from pathlib import Path
from typing import Dict
from typing import Generator

import pytest

from openapi_python_generator.version_detector import detect_openapi_version
from openapi_python_generator.parsers import parse_openapi_3_0, parse_openapi_3_1

test_data_folder = Path(__file__).parent / "test_data"
test_data_path = test_data_folder / "test_api.json"
test_result_path = Path(__file__).parent / "test_result"


@pytest.fixture(name="json_data")
def json_data_fixture() -> Generator[Dict, None, None]:
    with open(test_data_path) as f:
        yield json.load(f)


@pytest.fixture(name="model_data")
def model_data_fixture(json_data):
    """Parse OpenAPI spec with version-aware parser."""
    version = detect_openapi_version(json_data)
    if version == "3.0":
        yield parse_openapi_3_0(json_data)
    elif version == "3.1":
        yield parse_openapi_3_1(json_data)
    else:
        raise ValueError(f"Unsupported OpenAPI version: {version}")


@pytest.fixture(name="model_data_with_cleanup")
def model_data_with_cleanup_fixture(model_data):
    yield model_data

    # delete path test_result folder
    if test_result_path.exists():
        # delete folder and all subfolders
        shutil.rmtree(test_result_path)

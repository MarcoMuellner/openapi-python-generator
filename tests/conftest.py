import json
import shutil
from pathlib import Path
from typing import Dict
from typing import Generator

import pytest
from openapi_pydantic.v3.v3_0 import OpenAPI
from pydantic import ValidationError

test_data_folder = Path(__file__).parent / "test_data"
test_data_path = test_data_folder / "test_api.json"
test_result_path = Path(__file__).parent / "test_result"


@pytest.fixture(name="json_data")
def json_data_fixture() -> Generator[Dict, None, None]:
    with open(test_data_path) as f:
        yield json.load(f)


@pytest.fixture(name="model_data")
def model_data_fixture(json_data) -> OpenAPI:  # type: ignore
    yield OpenAPI(**json_data)


@pytest.fixture(name="model_data_with_cleanup")
def model_data_with_cleanup_fixture(model_data) -> OpenAPI:  # type: ignore
    yield model_data

    # delete path test_result folder
    if test_result_path.exists():
        # delete folder and all subfolders
        shutil.rmtree(test_result_path)

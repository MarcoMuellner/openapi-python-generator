import json
import shutil
from pathlib import Path
from typing import Dict
from typing import Generator
from openapi_python_generator.language_converters.python import common

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


@pytest.fixture
def with_orjson_enabled():
    """
    Fixture to enable orjson for the duration of the test
    """
    orjson_usage = common.get_use_orjson()
    common.set_use_orjson(True)
    try:
        yield
    finally:
        common.set_use_orjson(orjson_usage)

@pytest.fixture
def with_orjson_disabled():
    """
    Fixture to enable orjson for the duration of the test
    """
    orjson_usage = common.get_use_orjson()
    common.set_use_orjson(False)
    try:
        yield
    finally:
        common.set_use_orjson(orjson_usage)

@pytest.fixture
def with_pydantic_v1():
    """
    Fixture to set pydantic to v1 for the duration of the test
    """
    pydantic_version = common.get_pydantic_version()
    common.set_pydantic_version(common.PydanticVersion.V1)
    try:
        yield
    finally:
        common.set_pydantic_version(pydantic_version)

@pytest.fixture
def with_pydantic_v2():
    """
    Fixture to set pydantic to v2 for the duration of the test
    """
    pydantic_version = common.get_pydantic_version()
    common.set_pydantic_version(common.PydanticVersion.V2)
    try:
        yield
    finally:
        common.set_pydantic_version(pydantic_version)

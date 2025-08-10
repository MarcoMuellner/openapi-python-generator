from pathlib import Path
import shutil
import subprocess

import orjson
import pytest
import yaml
from httpx import ConnectError
from pydantic import ValidationError

from openapi_python_generator.common import FormatOptions, Formatter, HTTPLibrary
from openapi_python_generator.common import library_config_dict
from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.generate_data import get_open_api
from openapi_python_generator.generate_data import write_data
from openapi_python_generator.language_converters.python.generator import generator
from tests.conftest import test_data_folder
from tests.conftest import test_data_path
from tests.conftest import test_result_path


def test_get_open_api(model_data):
    # Test JSON file - get_open_api now returns (OpenAPI, version) tuple
    openapi_obj, version = get_open_api(test_data_path)
    assert openapi_obj == model_data
    assert version == "3.0"  # test_api.json is OpenAPI 3.0.2

    # Create YAML version of the test file
    yaml_path = test_data_path.with_suffix(".yaml")
    with open(test_data_path) as f:
        json_content = orjson.loads(f.read())
    with open(yaml_path, "w") as f:
        yaml.dump(json_content, f)

    # Test YAML file
    yaml_openapi_obj, yaml_version = get_open_api(yaml_path)
    assert yaml_openapi_obj == model_data
    assert yaml_version == "3.0"

    # Cleanup YAML file
    yaml_path.unlink()

    # Test remote file failure
    with pytest.raises(ConnectError):
        get_open_api("http://localhost:8080/api/openapi.json")

    # Test invalid OpenAPI spec
    with pytest.raises(ValidationError):
        get_open_api(test_data_folder / "failing_api.json")

    # Test non-existent file
    with pytest.raises(FileNotFoundError):
        get_open_api(test_data_folder / "file_does_not_exist.json")


def test_generate_data(model_data_with_cleanup):
    generate_data(test_data_path, test_result_path)
    assert test_result_path.exists()
    assert test_result_path.is_dir()
    assert (test_result_path / "api_config.py").exists()
    assert (test_result_path / "models").exists()
    assert (test_result_path / "models").is_dir()
    assert (test_result_path / "services").exists()
    assert (test_result_path / "services").is_dir()
    assert (test_result_path / "models" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").is_file()
    assert (test_result_path / "models" / "__init__.py").is_file()
    assert (test_result_path / "__init__.py").exists()
    assert (test_result_path / "__init__.py").is_file()


def test_write_data(model_data_with_cleanup):
    result = generator(model_data_with_cleanup, library_config_dict[HTTPLibrary.httpx])
    write_data(result, test_result_path, Formatter.BLACK)

    assert test_result_path.exists()
    assert test_result_path.is_dir()
    assert (test_result_path / "api_config.py").exists()
    assert (test_result_path / "models").exists()
    assert (test_result_path / "models").is_dir()
    assert (test_result_path / "services").exists()
    assert (test_result_path / "services").is_dir()
    assert (test_result_path / "models" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").is_file()
    assert (test_result_path / "models" / "__init__.py").is_file()
    assert (test_result_path / "__init__.py").exists()
    assert (test_result_path / "__init__.py").is_file()

    # delete test_result_path folder
    shutil.rmtree(test_result_path)

    model_data_copy = model_data_with_cleanup.model_copy()
    model_data_copy.components = None
    model_data_copy.paths = None

    result = generator(model_data_copy, library_config_dict[HTTPLibrary.httpx])
    write_data(result, test_result_path, Formatter.BLACK)

    assert test_result_path.exists()
    assert test_result_path.is_dir()
    assert (test_result_path / "api_config.py").exists()
    assert (test_result_path / "models").exists()
    assert (test_result_path / "models").is_dir()
    assert (test_result_path / "services").exists()
    assert (test_result_path / "services").is_dir()
    assert (test_result_path / "models" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").is_file()
    assert (test_result_path / "models" / "__init__.py").is_file()
    assert (test_result_path / "__init__.py").exists()
    assert (test_result_path / "__init__.py").is_file()


def test_write_formatted_data(model_data_with_cleanup):
    result = generator(model_data_with_cleanup, library_config_dict[HTTPLibrary.httpx])

    # First write code without formatter
    write_data(result, test_result_path, Formatter.NONE)

    assert test_result_path.exists()
    assert test_result_path.is_dir()
    assert (test_result_path / "api_config.py").exists()
    assert (test_result_path / "models").exists()
    assert (test_result_path / "models").is_dir()
    assert (test_result_path / "services").exists()
    assert (test_result_path / "services").is_dir()
    assert (test_result_path / "models" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").is_file()
    assert (test_result_path / "models" / "__init__.py").is_file()
    assert (test_result_path / "__init__.py").exists()
    assert (test_result_path / "__init__.py").is_file()

    assert not files_are_black_formatted(test_result_path)

    # delete test_result_path folder
    shutil.rmtree(test_result_path)

    model_data_copy = model_data_with_cleanup.model_copy()
    model_data_copy.components = None
    model_data_copy.paths = None

    result = generator(model_data_copy, library_config_dict[HTTPLibrary.httpx])
    write_data(result, test_result_path, Formatter.BLACK)

    assert test_result_path.exists()
    assert test_result_path.is_dir()
    assert (test_result_path / "api_config.py").exists()
    assert (test_result_path / "models").exists()
    assert (test_result_path / "models").is_dir()
    assert (test_result_path / "services").exists()
    assert (test_result_path / "services").is_dir()
    assert (test_result_path / "models" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").exists()
    assert (test_result_path / "services" / "__init__.py").is_file()
    assert (test_result_path / "models" / "__init__.py").is_file()
    assert (test_result_path / "__init__.py").exists()
    assert (test_result_path / "__init__.py").is_file()

    assert files_are_black_formatted(test_result_path)


def files_are_black_formatted(test_result_path: Path) -> bool:
    # Run the `black --check` command on all files. This does not write any file.
    result = subprocess.run(
        [
            "black",
            "--check",
            # Overwrite any exclusion due to a .gitignore.
            "--exclude",
            "''",
            # Settings also used when formatting the code when writing it
            "--fast" if FormatOptions.skip_validation else "--safe",
            "--line-length",
            str(FormatOptions.line_length),
            # The source directory
            str(test_result_path.absolute()),
        ],
        capture_output=True,
        text=True,
    )

    # With `--check` the return status has the following meaning:
    # - Return code 0 means nothing would change.
    # - Return code 1 means some files would be reformatted.
    # - Return code 123 means there was an internal error.

    if result.returncode == 123:
        result.check_returncode  # raise the error

    return result.returncode == 0

import pytest

from openapi_python_generator.generate_data import get_open_api, write_data
from openapi_python_generator.language_converters.python.generator import generator
from tests.conftest import test_data_path, test_result_path


def test_get_open_api(model_data):
    assert get_open_api(test_data_path) == model_data


def test_write_data(model_data_with_cleanup):
    result = generator(model_data_with_cleanup)
    write_data(result, test_result_path)

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

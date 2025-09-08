import pytest

from openapi_python_generator.version_detector import (
    detect_openapi_version,
    is_openapi_30,
    is_openapi_31,
)


@pytest.mark.parametrize(
    "spec, error",
    [
        (None, "must be a dictionary"),
        ([], "must be a dictionary"),
        ({}, "Missing required 'openapi' field"),
        ({"openapi": 3}, "'openapi' field must be a string"),
        ({"openapi": ""}, "'openapi' field cannot be empty"),
        ({"openapi": "2.0.0"}, "Unsupported OpenAPI version"),
        ({"openapi": "4.0.0"}, "Unsupported OpenAPI version"),
    ],
)
def test_detect_openapi_version_errors(spec, error):
    with pytest.raises(ValueError) as exc:
        detect_openapi_version(spec)  # type: ignore[arg-type]
    assert error in str(exc.value)


@pytest.mark.parametrize(
    "version",
    ["3.0.0", "3.0.1", "3.0.5", "3.0.10"],
)
def test_detect_openapi_version_30(version):
    assert detect_openapi_version({"openapi": version}) == "3.0"
    assert is_openapi_30({"openapi": version}) is True
    assert is_openapi_31({"openapi": version}) is False


@pytest.mark.parametrize(
    "version",
    ["3.1.0", "3.1.1", "3.1.5", "3.1.10"],
)
def test_detect_openapi_version_31(version):
    assert detect_openapi_version({"openapi": version}) == "3.1"
    assert is_openapi_31({"openapi": version}) is True
    assert is_openapi_30({"openapi": version}) is False


def test_is_helpers_invalid_spec():
    # Should swallow errors and return False
    assert is_openapi_30({}) is False
    assert is_openapi_31({}) is False

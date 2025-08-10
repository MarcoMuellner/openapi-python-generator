import json
from pathlib import Path

import pytest
from httpx import ConnectError

from openapi_python_generator.common import Formatter
from openapi_python_generator.generate_data import get_open_api


def test_get_open_api_file_not_found(tmp_path: Path):
    missing = tmp_path / "nope.json"
    with pytest.raises(FileNotFoundError):
        get_open_api(str(missing))


def test_get_open_api_unsupported_version(tmp_path: Path):
    spec = {"openapi": "4.0.0", "info": {"title": "x", "version": "1"}, "paths": {}}
    file_path = tmp_path / "spec.json"
    file_path.write_text(json.dumps(spec))
    # Unsupported version currently raises ValueError from version detection
    with pytest.raises(ValueError):
        get_open_api(str(file_path))


def test_generate_data_invalid_version(tmp_path: Path, monkeypatch):
    spec = {
        "openapi": "3.0.0",
        "info": {"title": "x", "version": "1"},
        "paths": {},
    }
    spec_path = tmp_path / "spec.json"
    spec_path.write_text(json.dumps(spec))

    import openapi_python_generator.generate_data as gd

    monkeypatch.setattr(gd, "detect_openapi_version", lambda d: "2.5")
    with pytest.raises(ValueError):
        gd.generate_data(str(spec_path), tmp_path / "out", formatter=Formatter.NONE)


def test_get_open_api_connect_error(monkeypatch):
    url = "https://example.com/spec.json"
    import httpx

    def _raise_connect(url_arg):  # noqa: ARG001
        raise ConnectError("boom")

    monkeypatch.setattr(httpx, "get", _raise_connect)
    with pytest.raises(ConnectError):
        get_open_api(url)

"""Test static file generation and inclusion."""

import tempfile
from pathlib import Path

from openapi_python_generator.common import Formatter
from openapi_python_generator.generate_data import write_data
from openapi_python_generator.models import ConversionResult, APIConfig, StaticFile


def test_static_files_are_written():
    """Test that static files are written to the output directory."""
    # Create a minimal ConversionResult with static files
    result = ConversionResult(
        models=[],
        services=[],
        api_config=APIConfig(
            file_name="api_config",
            base_url="https://api.example.com",
            content="class APIConfig:\n    pass\n",
        ),
        static_files=[
            StaticFile(
                file_name="errors",
                content='"""Error types."""\nclass APIError(Exception):\n    pass\n',
            ),
            StaticFile(
                file_name="response",
                content='"""Response wrapper."""\nclass DetailedResponse:\n    pass\n',
            ),
        ],
    )

    # Write to temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "generated"
        write_data(result, output_path, Formatter.NONE)

        # Verify static files were created
        assert (output_path / "errors.py").exists()
        assert (output_path / "response.py").exists()

        # Verify content
        errors_content = (output_path / "errors.py").read_text()
        assert "class APIError" in errors_content

        response_content = (output_path / "response.py").read_text()
        assert "class DetailedResponse" in response_content


def test_empty_static_files():
    """Test that empty static files list doesn't cause issues."""
    result = ConversionResult(
        models=[],
        services=[],
        api_config=APIConfig(
            file_name="api_config",
            base_url="https://api.example.com",
            content="class APIConfig:\n    pass\n",
        ),
        static_files=[],  # Empty list
    )

    # Write to temp directory
    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "generated"
        write_data(result, output_path, Formatter.NONE)

        # Verify basic structure still created
        assert (output_path / "api_config.py").exists()
        assert (output_path / "__init__.py").exists()
        assert (output_path / "models").is_dir()
        assert (output_path / "services").is_dir()

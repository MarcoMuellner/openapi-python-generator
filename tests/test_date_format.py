"""Test support for date-only format (datetime.date type)."""
import tempfile
from pathlib import Path

from openapi_python_generator.common import Formatter, HTTPLibrary
from openapi_python_generator.generate_data import generate_data


def test_date_format_generates_date_type():
    """Test that string fields with format='date' generate datetime.date type."""
    # OpenAPI spec with date format
    spec_path = Path(__file__).parent / "test_data" / "test_date_format.json"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "generated"

        # Generate code
        generate_data(
            spec_path,
            output_path,
            HTTPLibrary.httpx,
            use_orjson=True,  # date format handling requires orjson
        )

        # Read generated Person model
        person_model_path = output_path / "models" / "person.py"
        assert person_model_path.exists(), "Person model should be generated"

        person_model_content = person_model_path.read_text()

        # Verify import from datetime
        assert "from datetime import date, datetime" in person_model_content or (
            "from datetime import date" in person_model_content
            and "from datetime import datetime" in person_model_content
        ), "Should import date from datetime"

        # Verify birth_date field uses date type
        assert "birth_date: date" in person_model_content, (
            "birth_date with format='date' should use date type"
        )

        # Verify created_at field uses datetime type (to confirm date-time still works)
        assert "created_at: datetime" in person_model_content, (
            "created_at with format='date-time' should use datetime type"
        )


def test_date_format_without_orjson():
    """Test that date format falls back to str when orjson is not enabled."""
    spec_path = Path(__file__).parent / "test_data" / "test_date_format.json"

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "generated"

        # Generate code WITHOUT orjson
        generate_data(
            spec_path,
            output_path,
            HTTPLibrary.httpx,
            use_orjson=False,  # date format handling requires orjson
        )

        # Read generated Person model
        person_model_path = output_path / "models" / "person.py"
        person_model_content = person_model_path.read_text()

        # Without orjson, date should fall back to str
        assert "birth_date: str" in person_model_content, (
            "Without orjson, date format should fall back to str"
        )

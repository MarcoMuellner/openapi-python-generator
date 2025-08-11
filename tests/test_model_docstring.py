from openapi_pydantic.v3 import Schema, Components, DataType

from openapi_python_generator.language_converters.python.model_generator import generate_models
from openapi_python_generator.common import PydanticVersion


def test_model_docstring_title_used_when_present_and_fallback_to_name():
    """Ensure we prefer schema.title when present, fallback to schema name, and never emit 'None model'."""
    widget_schema = Schema(  # type: ignore[arg-type]
        type=DataType.OBJECT,
        title="Fancy Widget",
        properties={"id": Schema(type=DataType.INTEGER)},  # type: ignore[arg-type]
    )
    no_title_schema = Schema(  # type: ignore[arg-type]
        type=DataType.OBJECT,
        properties={"name": Schema(type=DataType.STRING)},  # type: ignore[arg-type]
    )

    components = Components(schemas={"Widget": widget_schema, "NoTitle": no_title_schema})  # type: ignore[arg-type]
    models = {m.file_name: m for m in generate_models(components, PydanticVersion.V2)}

    widget_content = models["Widget"].content
    notitle_content = models["NoTitle"].content

    assert "Fancy Widget model" in widget_content  # title used
    assert "NoTitle model" in notitle_content  # fallback used
    assert "None model" not in widget_content
    assert "None model" not in notitle_content

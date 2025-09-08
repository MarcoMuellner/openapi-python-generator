from openapi_pydantic.v3 import Response, MediaType, Schema, DataType, Operation
from openapi_python_generator.language_converters.python import service_generator
from openapi_python_generator.models import OpReturnType


def test_is_schema_type_helper():
    # Ensure the helper function body executes
    assert service_generator.is_schema_type(Schema(type=DataType.STRING)) is True


def test_generate_return_type_no_json_content():
    # Response with only text/plain should yield type None branch
    op = Operation(
        responses={
            "200": Response(
                description="",
                content={
                    "text/plain": MediaType(
                        media_type_schema=Schema(type=DataType.STRING)
                    )
                },
            )
        }
    )
    rt = service_generator.generate_return_type(op)
    assert isinstance(rt, OpReturnType)
    assert rt.type is None
    assert rt.complex_type is False

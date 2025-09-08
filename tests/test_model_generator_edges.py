import pytest
from openapi_pydantic.v3 import Schema, DataType

from openapi_python_generator.language_converters.python import common
from openapi_python_generator.language_converters.python.model_generator import (
    type_converter,
)


def test_type_converter_allof_single():
    # Single allOf element path (len(conversions)==1)
    schema = Schema(allOf=[Schema(type=DataType.STRING)])
    tc = type_converter(schema, True)
    assert tc.converted_type == "str"


def test_type_converter_oneof_single():
    schema = Schema(oneOf=[Schema(type=DataType.INTEGER)])
    tc = type_converter(schema, True)
    assert tc.converted_type == "int"


@pytest.mark.parametrize(
    "schema_type_list,expected",
    [
        ([DataType.STRING, DataType.INTEGER], "Optional[str]"),
        ([DataType.ARRAY, DataType.STRING], "Optional[List[Any]]"),
        ([DataType.NULL, DataType.STRING], "Optional[None]"),
    ],
)
def test_type_converter_list_type(schema_type_list, expected):
    # When schema.type is a list (union-like) we take the first entry per implementation
    schema = Schema(type=schema_type_list)
    tc = type_converter(schema, False)
    assert tc.converted_type == expected


def test_type_converter_list_type_with_format_uuid_date():
    # Exercise uuid/date-time handling inside list-branch when use_orjson is enabled
    prev = common.get_use_orjson()
    common.set_use_orjson(True)
    try:
        schema_uuid = Schema(type=[DataType.STRING], schema_format="uuid4")
        assert type_converter(schema_uuid, True).converted_type == "UUID4"
        schema_dt = Schema(type=[DataType.STRING], schema_format="date-time")
        assert type_converter(schema_dt, True).converted_type == "datetime"
    finally:
        common.set_use_orjson(prev)


def test_type_converter_nested_allof_oneof_anyof():
    # Nested composite: outer allOf with inner oneOf and anyOf references
    inner_oneof = Schema(
        oneOf=[Schema(type=DataType.STRING), Schema(type=DataType.INTEGER)]
    )
    inner_anyof = Schema(
        anyOf=[Schema(type=DataType.BOOLEAN), Schema(type=DataType.NUMBER)]
    )
    outer = Schema(allOf=[inner_oneof, inner_anyof])
    tc = type_converter(outer, True)
    # Expect Tuple[...] combining Union[...] forms from nested composites
    assert tc.converted_type.startswith("Tuple[")
    assert (
        "Union[str,int]" in tc.converted_type or "Union[int,str]" in tc.converted_type
    )


def test_type_converter_self_reference_in_allof():
    # Self reference branch (import_types None path) by referencing model name
    ref_name = "MyModel"
    from openapi_pydantic.v3 import Reference

    schema = Schema(allOf=[Reference(ref=f"#/components/schemas/{ref_name}")])
    tc = type_converter(schema, True, model_name=ref_name)
    # Single conversion path returns bare quoted self type
    assert tc.converted_type == '"' + ref_name + '"'


def test_type_converter_mixed_ref_and_schema_anyof():
    from openapi_pydantic.v3 import Reference

    schema = Schema(
        anyOf=[
            Reference(ref="#/components/schemas/OtherModel"),
            Schema(type=DataType.ARRAY, items=Schema(type=DataType.STRING)),
        ]
    )
    tc = type_converter(schema, False)
    # Optional Union containing OtherModel and List[str]
    assert tc.converted_type.startswith("Optional[Union[")
    assert "OtherModel" in tc.converted_type
    assert "List[str]" in tc.converted_type


def test_type_converter_allof_only_references_optional():
    # allOf with only references and outer required False -> Optional[Tuple[...]]
    from openapi_pydantic.v3 import Reference

    schema = Schema(
        allOf=[
            Reference(ref="#/components/schemas/AModel"),
            Reference(ref="#/components/schemas/BModel"),
        ]
    )
    tc = type_converter(schema, False)
    assert tc.converted_type.startswith("Optional[Tuple[")
    assert "AModel" in tc.converted_type and "BModel" in tc.converted_type


def test_type_converter_anyof_single():
    # anyOf single element should collapse to that element's converted type
    schema = Schema(anyOf=[Schema(type=DataType.BOOLEAN)])
    tc = type_converter(schema, True)
    assert tc.converted_type == "bool"


def test_type_converter_unknown_list_first_type_fallback():
    # Invalid enum value in list should raise ValidationError (spec invalid)
    from pydantic import ValidationError

    # Mixing unknown string with enum should raise ValidationError during model validation
    with pytest.raises(ValidationError):
        Schema(type=["mystery", DataType.STRING])  # type: ignore[arg-type]


def test_type_converter_allof_single_reference_self_optional():
    # allOf with single self reference and required False -> Optional["ModelName"]
    from openapi_pydantic.v3 import Reference

    name = "SelfRefModel"
    schema = Schema(allOf=[Reference(ref=f"#/components/schemas/{name}")])
    tc = type_converter(schema, False, model_name=name)
    assert tc.converted_type == f'Optional["{name}"]'

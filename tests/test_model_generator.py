import pytest
from openapi_schema_pydantic import Schema, Reference, OpenAPI

from openapi_python_generator.language_converters.python.model_generator import type_converter, \
    _generate_property_from_schema, _generate_property_from_reference, generate_models
from openapi_python_generator.models import Property, Model


@pytest.mark.parametrize("test_openapi_types,expected_python_types", [
    (Schema(type='string'), "str"),
    (Schema(type='integer'), "int"),
    (Schema(type='number'), "float"),
    (Schema(type='boolean'), "bool"),
    (Schema(type='array'), "List[Any]"),
    (Schema(type='array', items=Schema(type='string')), "List[str]"),
    (Schema(type='array', items=Reference(ref='#/components/schemas/test_name')), "List[test_name]"),
    (Schema(type='object'), "Dict[str, Any]"),
    (Schema(type='null'), "Any"),
])
def test_type_converter_simple(test_openapi_types, expected_python_types):
    assert type_converter(test_openapi_types, True) == expected_python_types
    assert type_converter(test_openapi_types, False) == 'Optional[' + expected_python_types + ']'


@pytest.mark.parametrize("test_openapi_types,expected_python_types", [
    (["string", "integer"], "str,int"),
    (["string", "integer", "number"], "str,int,float"),
    (["string", "integer", "number", "boolean"], "str,int,float,bool"),
    (["string", "integer", "number", "boolean", "array"], "str,int,float,bool,List[Any]")
])
def test_type_converter_of_type(test_openapi_types, expected_python_types):
    # Generate Schema object from test_openapi_types
    schema = Schema(allOf=[Schema(type=i) for i in test_openapi_types])

    assert type_converter(schema, True) == 'Tuple[' + expected_python_types + ']'
    assert type_converter(schema, False) == 'Optional[Tuple[' + expected_python_types + ']]'

    schema = Schema(oneOf=[Schema(type=i) for i in test_openapi_types])

    assert type_converter(schema, True) == 'Union[' + expected_python_types + ']'
    assert type_converter(schema, False) == 'Optional[Union[' + expected_python_types + ']]'

    schema = Schema(anyOf=[Schema(type=i) for i in test_openapi_types])

    assert type_converter(schema, True) == 'Union[' + expected_python_types + ']'
    assert type_converter(schema, False) == 'Optional[Union[' + expected_python_types + ']]'


def test_type_converter_exceptions():
    with pytest.raises(TypeError):
        type_converter(Schema(type="unknown"), True)

    with pytest.raises(TypeError):
        type_converter(Schema(type="array", items=Schema(type="unknown")), False)


@pytest.mark.parametrize("test_name, test_schema, test_parent_schema, expected_property", [
    ("test_name", Schema(type="string"), Schema(type="object"),
     Property(name="test_name", type="Optional[str]", required=False, default='None')),
    ("test_name", Schema(type="string"), Schema(type="object", required=["test_name"]),
     Property(name="test_name", type="str", required=True)),
])
def test_type_converter_property(test_name, test_schema, test_parent_schema, expected_property):
    assert _generate_property_from_schema(test_name, test_schema, test_parent_schema) == expected_property


@pytest.mark.parametrize("test_name, test_reference, parent_schema, expected_property, expected_model", [
    ("test_name", Reference(ref="#/components/schemas/test_name"), Schema(type="object"),
     Property(name="test_name", type="Optional[test_name]", required=False, default='None'), 'test_name'),
    ("test_name", Reference(ref="#/components/schemas/test_name"), Schema(type="object", required=["test_name"]),
     Property(name="test_name", type="test_name", required=True, default=None), 'test_name')
])
def test_type_converter_property_reference(test_name, test_reference, parent_schema, expected_property, expected_model):
    assert _generate_property_from_reference(test_name, test_reference,
                                             parent_schema) == (expected_property, expected_model)


def test_model_generation(model_data: OpenAPI):
    result = generate_models(model_data.components)

    assert len(result) == len(model_data.components.schemas.keys())
    for i in result:
        assert isinstance(i, Model)
        assert i.content is not None

        compile(i.content, '<string>', 'exec')

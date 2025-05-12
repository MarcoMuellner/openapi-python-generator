import pytest
from openapi_pydantic.v3.v3_0 import Schema, Reference, DataType, OpenAPI

from openapi_python_generator.common import PydanticVersion
from openapi_python_generator.language_converters.python import common
from openapi_python_generator.language_converters.python.model_generator import (
    _generate_property_from_reference,
)
from openapi_python_generator.language_converters.python.model_generator import (
    _generate_property_from_schema,
)
from openapi_python_generator.language_converters.python.model_generator import (
    generate_models,
)
from openapi_python_generator.language_converters.python.model_generator import (
    type_converter,
)
from openapi_python_generator.models import Model
from openapi_python_generator.models import Property
from openapi_python_generator.models import TypeConversion


@pytest.mark.parametrize(
    "test_openapi_types,expected_python_types",
    [
        (
            Schema(type=DataType.STRING),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.INTEGER),
            TypeConversion(original_type="integer", converted_type="int"),
        ),
        (
            Schema(type=DataType.NUMBER),
            TypeConversion(original_type="number", converted_type="float"),
        ),
        (
            Schema(type=DataType.BOOLEAN),
            TypeConversion(original_type="boolean", converted_type="bool"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="date-time"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="date"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="decimal"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.OBJECT),
            TypeConversion(original_type="object", converted_type="Dict[str, Any]"),
        ),
        (
            Schema(type=DataType.ARRAY),
            TypeConversion(original_type="array<unknown>", converted_type="List[Any]"),
        ),
        (
            Schema(type=DataType.ARRAY, items=Schema(type=DataType.STRING)),
            TypeConversion(original_type="array<string>", converted_type="List[str]"),
        ),
        (
            Schema(type=DataType.ARRAY, items=Reference(ref="#/components/schemas/test_name")),
            TypeConversion(
                original_type="array<#/components/schemas/test_name>",
                converted_type="List[test_name]",
                import_types=["from .test_name import test_name"],
            ),
        ),
        (
            Schema(type=None),
            TypeConversion(original_type="object", converted_type="Any"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid1"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid3"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid4"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid5"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
    ],
)
def test_type_converter_pydanticv1(test_openapi_types, expected_python_types, with_orjson_disabled, with_pydantic_v1):
    """
    Test base case with pydantic v1 and orjson disabled
    """
    assert type_converter(test_openapi_types, True) == expected_python_types

    if test_openapi_types.type == "array" and isinstance(
        test_openapi_types.items, Reference
    ):
        expected_type = expected_python_types.converted_type.split("[")[-1].split("]")[
            0
        ]

        assert (
            type_converter(test_openapi_types, False).converted_type
            == "Optional[List[Optional[" + expected_type + "]]]"
        )
    else:
        assert (
            type_converter(test_openapi_types, False).converted_type
            == "Optional[" + expected_python_types.converted_type + "]"
        )

@pytest.mark.parametrize(
    "test_openapi_types,expected_python_types",
    [
        (
            Schema(type=DataType.STRING),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.INTEGER),
            TypeConversion(original_type="integer", converted_type="int"),
        ),
        (
            Schema(type=DataType.NUMBER),
            TypeConversion(original_type="number", converted_type="float"),
        ),
        (
            Schema(type=DataType.BOOLEAN),
            TypeConversion(original_type="boolean", converted_type="bool"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="date-time"),
            TypeConversion(
                original_type="string",
                converted_type="datetime",
                import_types=["from datetime import datetime"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="date"),
            TypeConversion(
                original_type="string",
                converted_type="date",
                import_types=["from datetime import date"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="decimal"),
            TypeConversion(
                original_type="string",
                converted_type="Decimal",
                import_types=["from decimal import Decimal"],
            ),
        ),
        (
            Schema(type=DataType.OBJECT),
            TypeConversion(original_type="object", converted_type="Dict[str, Any]"),
        ),
        (
            Schema(type=DataType.ARRAY),
            TypeConversion(original_type="array<unknown>", converted_type="List[Any]"),
        ),
        (
            Schema(type=DataType.ARRAY, items=Schema(type=DataType.STRING)),
            TypeConversion(original_type="array<string>", converted_type="List[str]"),
        ),
        (
            Schema(type=DataType.ARRAY, items=Reference(ref="#/components/schemas/test_name")),
            TypeConversion(
                original_type="array<#/components/schemas/test_name>",
                converted_type="List[test_name]",
                import_types=["from .test_name import test_name"],
            ),
        ),
        (
            Schema(type=None),
            TypeConversion(original_type="object", converted_type="Any"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid"),
            TypeConversion(
                original_type="string",
                converted_type="UUID",
                import_types=["from uuid import UUID"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid1"),
            TypeConversion(
                original_type="string",
                converted_type="UUID1",
                import_types=["from pydantic import UUID1"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid3"),
            TypeConversion(
                original_type="string",
                converted_type="UUID3",
                import_types=["from pydantic import UUID3"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid4"),
            TypeConversion(
                original_type="string",
                converted_type="UUID4",
                import_types=["from pydantic import UUID4"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid5"),
            TypeConversion(
                original_type="string",
                converted_type="UUID5",
                import_types=["from pydantic import UUID5"],
            ),
        ),
    ],
)
def test_type_converter_pydanticv2(test_openapi_types, expected_python_types, with_orjson_disabled, with_pydantic_v2):
    """
    Test base case with pydantic v2 and orjson disabled
    """
    assert type_converter(test_openapi_types, True) == expected_python_types

    if test_openapi_types.type == "array" and isinstance(
        test_openapi_types.items, Reference
    ):
        expected_type = expected_python_types.converted_type.split("[")[-1].split("]")[
            0
        ]

        assert (
            type_converter(test_openapi_types, False).converted_type
            == "Optional[List[Optional[" + expected_type + "]]]"
        )
    else:
        assert (
            type_converter(test_openapi_types, False).converted_type
            == "Optional[" + expected_python_types.converted_type + "]"
        )


@pytest.mark.parametrize(
    "test_openapi_types,expected_python_types",
    [
        (
            Schema(type=DataType.STRING),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.INTEGER),
            TypeConversion(original_type="integer", converted_type="int"),
        ),
        (
            Schema(type=DataType.NUMBER),
            TypeConversion(original_type="number", converted_type="float"),
        ),
        (
            Schema(type=DataType.BOOLEAN),
            TypeConversion(original_type="boolean", converted_type="bool"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="date-time"),
            TypeConversion(
                original_type="string",
                converted_type="datetime",
                import_types=["from datetime import datetime"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="date"),
            TypeConversion(
                original_type="string",
                converted_type="date",
                import_types=["from datetime import date"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="decimal"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="email"),
            TypeConversion(
                original_type="string",
                converted_type="str",
            ),
        ),
        (
            Schema(type=DataType.OBJECT),
            TypeConversion(original_type="object", converted_type="Dict[str, Any]"),
        ),
        (
            Schema(type=DataType.ARRAY),
            TypeConversion(original_type="array<unknown>", converted_type="List[Any]"),
        ),
        (
            Schema(type=DataType.ARRAY, items=Schema(type=DataType.STRING)),
            TypeConversion(original_type="array<string>", converted_type="List[str]"),
        ),
        (
            Schema(type=DataType.ARRAY, items=Reference(ref="#/components/schemas/test_name")),
            TypeConversion(
                original_type="array<#/components/schemas/test_name>",
                converted_type="List[test_name]",
                import_types=["from .test_name import test_name"],
            ),
        ),
        (
            Schema(type=None),
            TypeConversion(original_type="object", converted_type="Any"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid"),
            TypeConversion(
                original_type="string",
                converted_type="UUID",
                import_types=["from uuid import UUID"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid1"),
            TypeConversion(
                original_type="string",
                converted_type="UUID1",
                import_types=["from pydantic import UUID1"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid3"),
            TypeConversion(
                original_type="string",
                converted_type="UUID3",
                import_types=["from pydantic import UUID3"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid4"),
            TypeConversion(
                original_type="string",
                converted_type="UUID4",
                import_types=["from pydantic import UUID4"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid5"),
            TypeConversion(
                original_type="string",
                converted_type="UUID5",
                import_types=["from pydantic import UUID5"],
            ),
        ),
    ],
)
def test_type_converter_orjson_pydanticv1(test_openapi_types, expected_python_types, with_orjson_enabled, with_pydantic_v1):
    """
    Test type conversion with pydantic v1 and orjson enabled
    """
    assert type_converter(test_openapi_types, True) == expected_python_types
    if test_openapi_types.type == "array" and isinstance(
        test_openapi_types.items, Reference
    ):
        expected_type = expected_python_types.converted_type.split("[")[-1].split("]")[
            0
        ]

        assert (
            type_converter(test_openapi_types, False).converted_type
            == "Optional[List[Optional[" + expected_type + "]]]"
        )
    else:
        assert (
            type_converter(test_openapi_types, False).converted_type
            == "Optional[" + expected_python_types.converted_type + "]"
        )

@pytest.mark.parametrize(
    "test_openapi_types,expected_python_types",
    [
        (
            Schema(type=DataType.STRING),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.INTEGER),
            TypeConversion(original_type="integer", converted_type="int"),
        ),
        (
            Schema(type=DataType.NUMBER),
            TypeConversion(original_type="number", converted_type="float"),
        ),
        (
            Schema(type=DataType.BOOLEAN),
            TypeConversion(original_type="boolean", converted_type="bool"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="date-time"),
            TypeConversion(
                original_type="string",
                converted_type="datetime",
                import_types=["from datetime import datetime"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="date"),
            TypeConversion(
                original_type="string",
                converted_type="date",
                import_types=["from datetime import date"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="decimal"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="email"),
            TypeConversion(original_type="string", converted_type="str"),
        ),
        (
            Schema(type=DataType.OBJECT),
            TypeConversion(original_type="object", converted_type="Dict[str, Any]"),
        ),
        (
            Schema(type=DataType.ARRAY),
            TypeConversion(original_type="array<unknown>", converted_type="List[Any]"),
        ),
        (
            Schema(type=DataType.ARRAY, items=Schema(type=DataType.STRING)),
            TypeConversion(original_type="array<string>", converted_type="List[str]"),
        ),
        (
            Schema(type=DataType.ARRAY, items=Reference(ref="#/components/schemas/test_name")),
            TypeConversion(
                original_type="array<#/components/schemas/test_name>",
                converted_type="List[test_name]",
                import_types=["from .test_name import test_name"],
            ),
        ),
        (
            Schema(type=None),
            TypeConversion(original_type="object", converted_type="Any"),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid"),
            TypeConversion(
                original_type="string",
                converted_type="UUID",
                import_types=["from uuid import UUID"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid1"),
            TypeConversion(
                original_type="string",
                converted_type="UUID1",
                import_types=["from pydantic import UUID1"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid3"),
            TypeConversion(
                original_type="string",
                converted_type="UUID3",
                import_types=["from pydantic import UUID3"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid4"),
            TypeConversion(
                original_type="string",
                converted_type="UUID4",
                import_types=["from pydantic import UUID4"],
            ),
        ),
        (
            Schema(type=DataType.STRING, schema_format="uuid5"),
            TypeConversion(
                original_type="string",
                converted_type="UUID5",
                import_types=["from pydantic import UUID5"],
            ),
        ),
    ],
)
def test_type_converter_orjson_pydanticv2(test_openapi_types, expected_python_types, with_orjson_enabled, with_pydantic_v2):
    """
    Test type conversion with pydantic v2 and orjson enabled
    """
    assert type_converter(test_openapi_types, True) == expected_python_types
    if test_openapi_types.type == "array" and isinstance(
        test_openapi_types.items, Reference
    ):
        expected_type = expected_python_types.converted_type.split("[")[-1].split("]")[
            0
        ]

        assert (
            type_converter(test_openapi_types, False).converted_type
            == "Optional[List[Optional[" + expected_type + "]]]"
        )
    else:
        assert (
            type_converter(test_openapi_types, False).converted_type
            == "Optional[" + expected_python_types.converted_type + "]"
        )

def test_type_converter_all_of_reference():
    schema = Schema(
        allOf=[Reference(ref="#/components/schemas/test_name"), Schema(type=DataType.STRING)]
    )
    assert type_converter(schema, True).converted_type == "Tuple[test_name,str]"

    schema = Schema(
        oneOf=[Reference(ref="#/components/schemas/test_name"), Schema(type=DataType.STRING)]
    )
    assert type_converter(schema, True).converted_type == "Union[test_name,str]"


@pytest.mark.parametrize(
    "test_openapi_types,expected_python_types",
    [
        ([DataType.STRING, DataType.INTEGER], "str,int"),
        ([DataType.STRING, DataType.INTEGER, DataType.NUMBER], "str,int,float"),
        ([DataType.STRING, DataType.INTEGER, DataType.NUMBER, DataType.BOOLEAN], "str,int,float,bool"),
        (
            [DataType.STRING, DataType.INTEGER, DataType.NUMBER, DataType.BOOLEAN,DataType.ARRAY],
            "str,int,float,bool,List[Any]",
        ),
    ],
)
def test_type_converter_of_type(test_openapi_types, expected_python_types):
    # Generate Schema object from test_openapi_types
    schema = Schema(allOf=[Schema(type=i) for i in test_openapi_types])

    assert (
        type_converter(schema, True).converted_type
        == "Tuple[" + expected_python_types + "]"
    )
    assert (
        type_converter(schema, False).converted_type
        == "Optional[Tuple[" + expected_python_types + "]]"
    )

    schema = Schema(oneOf=[Schema(type=i) for i in test_openapi_types])

    assert (
        type_converter(schema, True).converted_type
        == "Union[" + expected_python_types + "]"
    )
    assert (
        type_converter(schema, False).converted_type
        == "Optional[Union[" + expected_python_types + "]]"
    )

    schema = Schema(anyOf=[Schema(type=i) for i in test_openapi_types])

    assert (
        type_converter(schema, True).converted_type
        == "Union[" + expected_python_types + "]"
    )
    assert (
        type_converter(schema, False).converted_type
        == "Optional[Union[" + expected_python_types + "]]"
    )


@pytest.mark.parametrize(
    "test_model_name, test_name, test_schema, test_parent_schema, expected_property",
    [
        (
            "SomeModel",
            "test_name",
            Schema(type=DataType.STRING),
            Schema(type=DataType.OBJECT),
            Property(
                name="test_name",
                type=TypeConversion(
                    original_type="string", converted_type="Optional[str]"
                ),
                required=False,
                default="None",
            ),
        ),
        (
            "SomeModel",
            "test_name",
            Schema(type=DataType.STRING),
            Schema(type=DataType.OBJECT, required=["test_name"]),
            Property(
                name="test_name",
                type=TypeConversion(original_type="string", converted_type="str"),
                required=True,
                import_type=["test_name"],
                default=None
            ),
        ),
        (
            "SomeModel",
            "SomeModel",
            Schema(allOf=[Reference(ref="#/components/schemas/SomeModel")]),
            Schema(type=DataType.OBJECT, required=["SomeModel"]),
            Property(
                name="SomeModel",
                type=TypeConversion(
                    original_type="tuple<#/components/schemas/SomeModel>",
                    converted_type='"SomeModel"',
                    import_types=[],
                ),
                required=True,
                import_type=[],
                default=None
            ),
        ),
    ],
)
def test_type_converter_property(
    test_model_name, test_name, test_schema, test_parent_schema, expected_property
):
    assert (
        _generate_property_from_schema(
            test_model_name, test_name, test_schema, test_parent_schema
        )
        == expected_property
    )


@pytest.mark.parametrize(
    "test_name, test_reference, parent_schema, expected_property",
    [
        (
            "test_name",
            Reference(ref="#/components/schemas/test_name"),
            Schema(type=DataType.OBJECT),
            Property(
                name="test_name",
                type=TypeConversion(
                    original_type="#/components/schemas/test_name",
                    converted_type="Optional[test_name]",
                    import_types=["from .test_name import test_name"],
                ),
                required=False,
                default="None",
                import_type=["test_name"],
            ),
        ),
        (
            "test_name",
            Reference(ref="#/components/schemas/test_name"),
            Schema(type=DataType.OBJECT, required=["test_name"]),
            Property(
                name="test_name",
                type=TypeConversion(
                    original_type="#/components/schemas/test_name",
                    converted_type="test_name",
                    import_types=["from .test_name import test_name"],
                ),
                required=True,
                default=None,
                import_type=["test_name"],
            ),
        ),
    ],
)
def test_type_converter_property_reference(
    test_name, test_reference, parent_schema, expected_property
):
    assert (
        _generate_property_from_reference("", test_name, test_reference, parent_schema)
        == expected_property
    )

@pytest.mark.parametrize("pydantic_version", [PydanticVersion.V1, PydanticVersion.V2])
def test_model_generation(model_data: OpenAPI, pydantic_version : PydanticVersion):
    result = generate_models(model_data.components, pydantic_version)  # type: ignore

    assert len(result) == len(model_data.components.schemas.keys())  # type: ignore
    for i in result:
        assert isinstance(i, Model)
        assert i.content is not None

        compile(i.content, "<string>", "exec")

    model_data_copy = model_data.model_copy()
    model_data_copy.components.schemas = None  # type: ignore

    result = generate_models(model_data_copy.components, pydantic_version)  # type: ignore

    assert len(result) == 0

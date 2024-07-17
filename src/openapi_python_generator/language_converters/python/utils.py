import itertools
from typing import List, Optional
from caseconverter import pascalcase

import openapi_python_generator

from openapi_python_generator.language_converters.python import common
from openapi_python_generator.models import TypeConversion
from openapi_python_generator.models import Property
from openapi_python_generator.models import TypeConversion

if openapi_python_generator.OPENAPI_VERSION == "3.0":
    from openapi_pydantic.v3.v3_0_3.reference import Reference
    from openapi_pydantic.v3.v3_0_3.schema import Schema
    from openapi_pydantic.v3.v3_0_3.parameter import Parameter
else:
    from openapi_pydantic import Reference
    from openapi_pydantic import Schema
    from openapi_pydantic import Parameter


def _generate_property_from_reference(
    model_name: str,
    name: str,
    reference: Reference,
    parent_schema: Optional[Schema] = None,
    force_required: bool = False,
) -> Property:
    """
    Generates a property from a reference. It takes the name of the reference as the type, and then
    returns a property type
    :param name: Name of the schema
    :param reference: reference to be converted
    :param parent_schema: Component this belongs to
    :param force_required: Force the property to be required
    :return: Property and model to be imported by the file
    """
    required = (
        parent_schema is not None
        and parent_schema.required is not None
        and name in parent_schema.required
    ) or force_required
    import_model = common.normalize_symbol(reference.ref.split("/")[-1])
    import_model = pascalcase(import_model)

    if import_model == model_name:
        type_conv = TypeConversion(
            original_type=reference.ref,
            converted_type=(
                import_model if required else 'Optional["' + import_model + '"]'
            ),
            import_types=None,
        )
    else:
        type_conv = TypeConversion(
            original_type=reference.ref,
            converted_type=(
                import_model if required else "Optional[" + import_model + "]"
            ),
            import_types=[f"from .{import_model} import {import_model}"],
        )
    return Property(
        name=name,
        type=type_conv,
        required=required,
        default=None if required else "None",
        import_type=[import_model],
    )


def _generate_property_from_schema(
    model_name: str,
    name: str,
    schema: Schema,
    parent_schema: Optional[Schema] = None,
) -> Property:
    """
    Generates a property from a schema. It takes the type of the schema and converts it to a python type, and then
    creates the according property.
    :param model_name: Name of the model this property belongs to
    :param name: Name of the schema
    :param schema: schema to be converted
    :param parent_schema: Component this belongs to
    :return: Property
    """
    required = (
        parent_schema is not None
        and parent_schema.required is not None
        and name in parent_schema.required
    )
    return Property(
        name=name,
        type=type_converter(schema, required, model_name),
        required=required,
        default=None if required else "None",
    )


def _generate_property_from_paramter(
    model_name: str,
    name: str,
    parameter: Parameter,
    parent_schema: Optional[Schema] = None,
):
    return _generate_property_from_schema(
        model_name,
        name,
        parameter.param_schema,
        parent_schema,
    )


def type_converter(  # noqa: C901
    schema: Schema,
    required: bool = False,
    model_name: Optional[str] = None,
) -> TypeConversion:
    """
    Converts an OpenAPI type to a Python type.
    :param schema: Schema containing the type to be converted
    :param model_name: Name of the original model on which the type is defined
    :param required: Flag indicating if the type is required by the class
    :return: The converted type
    """
    if required:
        pre_type = ""
        post_type = ""
    else:
        pre_type = "Optional["
        post_type = "]"

    original_type = schema.type if schema.type is not None else "object"
    import_types: Optional[List[str]] = None

    if schema.allOf is not None:
        conversions = []
        for sub_schema in schema.allOf:
            if isinstance(sub_schema, Schema):
                conversions.append(type_converter(sub_schema, True))
            else:
                import_type = common.normalize_symbol(sub_schema.ref.split("/")[-1])
                import_type = pascalcase(import_type)
                if import_type == model_name:
                    conversions.append(
                        TypeConversion(
                            original_type=sub_schema.ref,
                            converted_type='"' + model_name + '"',
                            import_types=None,
                        )
                    )
                else:
                    import_types = [f"from .{import_type} import {import_type}"]
                    conversions.append(
                        TypeConversion(
                            original_type=sub_schema.ref,
                            converted_type=import_type,
                            import_types=import_types,
                        )
                    )

        original_type = (
            "tuple<" + ",".join([i.original_type for i in conversions]) + ">"
        )
        if len(conversions) == 1:
            converted_type = conversions[0].converted_type
        else:
            converted_type = (
                "Tuple[" + ",".join([i.converted_type for i in conversions]) + "]"
            )

        converted_type = pre_type + converted_type + post_type
        import_types = [
            i.import_types[0] for i in conversions if i.import_types is not None
        ]

    elif schema.oneOf is not None or schema.anyOf is not None:
        used = schema.oneOf if schema.oneOf is not None else schema.anyOf
        used = used if used is not None else []
        conversions = []
        for sub_schema in used:
            if isinstance(sub_schema, Schema):
                conversions.append(type_converter(sub_schema, True))
            else:
                import_type = pascalcase(sub_schema.ref.split("/")[-1])
                import_types = [f"from .{import_type} import {import_type}"]
                conversions.append(
                    TypeConversion(
                        original_type=sub_schema.ref,
                        converted_type=import_type,
                        import_types=import_types,
                    )
                )

        original_type = (
            "union<" + ",".join([i.original_type for i in conversions]) + ">"
        )

        if len(conversions) == 1:
            converted_type = conversions[0].converted_type
        else:
            converted_type = (
                "Union[" + ",".join([i.converted_type for i in conversions]) + "]"
            )

        converted_type = pre_type + converted_type + post_type
        import_types = list(
            itertools.chain(
                *[i.import_types for i in conversions if i.import_types is not None]
            )
        )
    # We only want to auto convert to datetime if orjson is used throghout the code, otherwise we can not
    # serialize it to JSON.
    elif schema.type == "string" and (
        schema.schema_format is None or not common.get_use_orjson()
    ):
        converted_type = pre_type + "str" + post_type
    elif (
        schema.type == "string"
        and schema.schema_format.startswith("uuid")
        and common.get_use_orjson()
    ):
        if len(schema.schema_format) > 4 and schema.schema_format[4].isnumeric():
            uuid_type = schema.schema_format.upper()
            converted_type = pre_type + uuid_type + post_type
            import_types = ["from pydantic import " + uuid_type]
        else:
            converted_type = pre_type + "UUID" + post_type
            import_types = ["from uuid import UUID"]
    elif schema.type == "string" and schema.schema_format == "date-time":
        converted_type = pre_type + "datetime" + post_type
        import_types = ["from datetime import datetime"]
    elif schema.type == "integer":
        converted_type = pre_type + "int" + post_type
    elif schema.type == "number":
        converted_type = pre_type + "float" + post_type
    elif schema.type == "boolean":
        converted_type = pre_type + "bool" + post_type
    elif schema.type == "array":
        retVal = pre_type + "List["
        if isinstance(schema.items, Reference):
            converted_reference = _generate_property_from_reference(
                model_name, "", schema.items, schema, required
            )
            import_types = converted_reference.type.import_types
            original_type = "array<" + converted_reference.type.original_type + ">"
            retVal += converted_reference.type.converted_type
        elif isinstance(schema.items, Schema):
            original_type = "array<" + str(schema.items.type) + ">"
            retVal += type_converter(schema.items, True).converted_type
        else:
            original_type = "array<unknown>"
            retVal += "Any"

        converted_type = retVal + "]" + post_type
    elif schema.type == "object":
        converted_type = pre_type + "Dict[str, Any]" + post_type
    elif schema.type == "null":
        converted_type = pre_type + "None" + post_type
    elif schema.type is None:
        converted_type = pre_type + "Any" + post_type
    else:
        raise TypeError(f"Unknown type: {schema.type}")

    return TypeConversion(
        original_type=original_type,
        converted_type=converted_type,
        import_types=import_types,
    )

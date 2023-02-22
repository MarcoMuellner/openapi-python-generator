import itertools
import re
from typing import List
from typing import Optional

import click
from openapi_schema_pydantic import Components
from openapi_schema_pydantic import Reference
from openapi_schema_pydantic import Schema

from openapi_python_generator.language_converters.python import common
from openapi_python_generator.language_converters.python.jinja_config import (
    ENUM_TEMPLATE,
)
from openapi_python_generator.language_converters.python.jinja_config import JINJA_ENV
from openapi_python_generator.language_converters.python.jinja_config import (
    MODELS_TEMPLATE,
)
from openapi_python_generator.models import Model
from openapi_python_generator.models import Property
from openapi_python_generator.models import TypeConversion


def type_converter(schema: Schema,  required: bool = False, model_name: Optional[str] = None,) -> TypeConversion:
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
                import_type = sub_schema.ref.split("/")[-1]
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
                import_type = sub_schema.ref.split("/")[-1]
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
            converted_reference = _generate_property_from_reference(model_name, "", schema.items, schema, required)
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
    elif schema.type is None or schema.type == "null":
        converted_type = pre_type + "Any" + post_type
    else:
        raise TypeError(f"Unknown type: {schema.type}")

    return TypeConversion(
        original_type=original_type,
        converted_type=converted_type,
        import_types=import_types,
    )


def _generate_property_from_schema(
    model_name : str, name: str, schema: Schema, parent_schema: Optional[Schema] = None
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


def _generate_property_from_reference(
        model_name: str, name: str, reference: Reference, parent_schema: Optional[Schema] = None, force_required: bool = False
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
    import_model = reference.ref.split("/")[-1]

    if import_model == model_name:
        type_conv = TypeConversion(
            original_type=reference.ref,
            converted_type=import_model if required else 'Optional["' + import_model + '"]',
            import_types=None
        )
    else:
        type_conv = TypeConversion(
            original_type=reference.ref,
            converted_type=import_model if required else "Optional[" + import_model + "]",
            import_types=[f"from .{import_model} import {import_model}"],
        )
    return Property(
        name=name,
        type=type_conv,
        required=required,
        default=None if required else "None",
        import_type=[import_model],
    )


def generate_models(components: Components) -> List[Model]:
    """
    Receives components from an OpenAPI 3.0 specification and generates the models from it.
    It does so, by iterating over the components.schemas dictionary. For each schema, it checks if
    it is a normal schema (i.e. simple type like string, integer, etc.), a reference to another schema, or
    an array of types/references. It then computes pydantic models from it using jinja2
    :param components: The components from an OpenAPI 3.0 specification.
    :return: A list of models.
    """
    models: List[Model] = []

    if components.schemas is None:
        return models

    for name, schema_or_reference in components.schemas.items():
        if schema_or_reference.enum is not None:
            value_dict = schema_or_reference.dict()
            regex = re.compile(r"[\s\/=\*\+]+")
            value_dict["enum"] = [
                re.sub(regex, "_", i) if isinstance(i, str) else f"value_{i}"
                for i in value_dict["enum"]
            ]
            m = Model(
                file_name=name,
                content=JINJA_ENV.get_template(ENUM_TEMPLATE).render(
                    name=name, **value_dict
                ),
                openapi_object=schema_or_reference,
                properties=[],
            )
            try:
                compile(m.content, "<string>", "exec")
                models.append(m)
            except SyntaxError as e:  # pragma: no cover
                click.echo(f"Error in model {name}: {e}")

            continue  # pragma: no cover

        properties = []
        property_iterator = (
            schema_or_reference.properties.items()
            if schema_or_reference.properties is not None
            else {}
        )
        for prop_name, property in property_iterator:
            if isinstance(property, Reference):
                conv_property = _generate_property_from_reference(
                    name, prop_name, property, schema_or_reference
                )
            else:
                conv_property = _generate_property_from_schema(
                    name, prop_name, property, schema_or_reference
                )
            properties.append(conv_property)

        generated_content = JINJA_ENV.get_template(MODELS_TEMPLATE).render(
            schema_name=name, schema=schema_or_reference, properties=properties
        )

        try:
            compile(generated_content, "<string>", "exec")
        except SyntaxError as e:  # pragma: no cover
            click.echo(f"Error in model {name}: {e}")  # pragma: no cover

        models.append(
            Model(
                file_name=name,
                content=generated_content,
                openapi_object=schema_or_reference,
                properties=properties,
            )
        )

    return models

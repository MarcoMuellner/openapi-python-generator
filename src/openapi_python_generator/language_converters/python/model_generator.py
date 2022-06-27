from typing import List, Optional

import click
from openapi_schema_pydantic import Components, Reference, Schema

from openapi_python_generator.language_converters.python.jinja_config import (
    JINJA_ENV,
    MODELS_TEMPLATE,
    ENUM_TEMPLATE,
)
from openapi_python_generator.models import Model, Property, TypeConversion


def type_converter(schema: Schema, required: bool = False) -> TypeConversion:
    """
    Converts an OpenAPI type to a Python type.
    :param schema: Schema containing the type to be converted
    :param required: Flag indicating if the type is required by the class
    :return: The converted type
    """
    if required:
        pre_type = ""
        post_type = ""
    else:
        pre_type = "Optional["
        post_type = "]"

    original_type = schema.type
    import_types = None

    if schema.allOf is not None:
        conversions = [type_converter(i, True) for i in schema.allOf]

        original_type = "tuple<" + ",".join([i.type for i in schema.allOf]) + ">"
        converted_type = (
            pre_type
            + "Tuple["
            + ",".join([i.converted_type for i in conversions])
            + "]"
            + post_type
        )
        import_types = [
            i.import_types for i in conversions if i.import_types is not None
        ]

    elif schema.oneOf is not None or schema.anyOf is not None:
        used = schema.oneOf if schema.oneOf is not None else schema.anyOf
        conversions = [type_converter(i, True) for i in used]
        original_type = "union<" + ",".join([i.type for i in used]) + ">"
        converted_type = (
            pre_type
            + "Union["
            + ",".join([i.converted_type for i in conversions])
            + "]"
            + post_type
        )
        import_types = [
            i.import_types for i in conversions if i.import_types is not None
        ]
    elif schema.type == "string":
        converted_type = pre_type + "str" + post_type
    elif schema.type == "integer":
        converted_type = pre_type + "int" + post_type
    elif schema.type == "number":
        converted_type = pre_type + "float" + post_type
    elif schema.type == "boolean":
        converted_type = pre_type + "bool" + post_type
    elif schema.type == "array":
        retVal = pre_type + "List["
        if isinstance(schema.items, Reference):
            import_types = [schema.items.ref.split("/")[-1]]
            original_type = "array<" + schema.items.ref.split("/")[-1] + ">"
            retVal += schema.items.ref.split("/")[-1]
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
    name: str, schema: Schema, parent_schema: Optional[Schema] = None
) -> Property:
    """
    Generates a property from a schema. It takes the type of the schema and converts it to a python type, and then
    creates the according property.
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
        type=type_converter(schema, required),
        required=required,
        default=None if required else "None",
    )


def _generate_property_from_reference(
    name: str, reference: Reference, parent_schema: Optional[Schema] = None
) -> Property:
    """
    Generates a property from a reference. It takes the name of the reference as the type, and then
    returns a property type
    :param name: Name of the schema
    :param reference: reference to be converted
    :param parent_schema: Component this belongs to
    :return: Property and model to be imported by the file
    """
    required = (
        parent_schema is not None
        and parent_schema.required is not None
        and name in parent_schema.required
    )
    import_model = reference.ref.split("/")[-1]

    type_conv = TypeConversion(
        original_type=reference.ref,
        converted_type=import_model if required else "Optional[" + import_model + "]",
        import_types=[import_model],
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
    models = []

    for name, schema in components.schemas.items():
        if schema.enum is not None:
            m = Model(
                file_name=name,
                content=JINJA_ENV.get_template(ENUM_TEMPLATE).render(
                    name=name, **schema.dict()
                ),
                openapi_object=schema,
                references=[],
                properties=[],
            )
            try:
                compile(m.content, "<string>", "exec")
                models.append(m)
            except SyntaxError as e:  # pragma: no cover
                click.echo(f"Error in model {name}: {e}")

            continue  # pragma: no cover

        properties = []
        for prop_name, property in schema.properties.items():
            if isinstance(property, Reference):
                conv_property = _generate_property_from_reference(
                    prop_name, property, schema
                )
            else:
                conv_property = _generate_property_from_schema(
                    prop_name, property, schema
                )
            properties.append(conv_property)

        generated_content = JINJA_ENV.get_template(MODELS_TEMPLATE).render(
            schema_name=name, schema=schema, properties=properties
        )

        try:
            compile(generated_content, "<string>", "exec")
        except SyntaxError as e:  # pragma: no cover
            click.echo(f"Error in model {name}: {e}")  # pragma: no cover

        models.append(
            Model(
                file_name=name,
                content=generated_content,
                openapi_object=schema,
                properties=properties,
            )
        )

    return models

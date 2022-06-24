from typing import List, Optional, Tuple

import typer
from openapi_schema_pydantic import Components, Reference, Schema

from openapi_python_generator.language_converters.python.jinja_config import JINJA_ENV, MODELS_TEMPLATE, ENUM_TEMPLATE
from openapi_python_generator.models import Model, Property

def type_converter(schema: Schema, required: bool = False) -> str:
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

    if schema.allOf is not None:
        return pre_type + "Tuple[" + ','.join(type_converter(i, True) for i in schema.allOf) + "]" + post_type
    elif schema.oneOf is not None or schema.anyOf is not None:
        used = schema.oneOf if schema.oneOf is not None else schema.anyOf
        return pre_type + "Union[" + ','.join(type_converter(i, True) for i in used) + "]" + post_type
    elif schema.type == "string":
        return pre_type + "str" + post_type
    elif schema.type == "integer":
        return pre_type + "int" + post_type
    elif schema.type == "number":
        return pre_type + "float" + post_type
    elif schema.type == "boolean":
        return pre_type + "bool" + post_type
    elif schema.type == "array":
        retVal = pre_type + "List["
        if isinstance(schema.items, Reference):
            retVal += schema.items.ref.split("/")[-1]
        elif isinstance(schema.items, Schema):
            retVal += type_converter(schema.items, True)
        else:
            retVal += "Any"

        return retVal + "]" + post_type
    elif schema.type == "object":
        return pre_type + "Dict[str, Any]" + post_type
    elif schema.type is None or schema.type == "null":
        return pre_type + "Any" + post_type
    else:
        raise TypeError(f"Unknown type: {schema.type}")


def _generate_property_from_schema(name: str, schema: Schema, parentSchema: Optional[Schema] = None) -> Property:
    """
    Generates a property from a schema. It takes the type of the schema and converts it to a python type, and then
    creates the according property.
    :param name: Name of the schema
    :param schema: schema to be converted
    :param parentSchema: Component this belongs to
    :return: Property
    """
    required = parentSchema.required is not None and name in parentSchema.required
    return Property(
        name=name,
        type=type_converter(schema, required),
        required=required,
        default=None if required else "None")


def _generate_property_from_reference(name: str, reference: Reference,
                                      parentSchema: Optional[Schema] = None) -> Tuple[
    Property, str]:
    """
    Generates a property from a reference. It takes the name of the reference as the type, and then
    returns a property type
    :param name: Name of the schema
    :param reference: reference to be converted
    :param parentSchema: Component this belongs to
    :return: Property and model to be imported by the file
    """
    required = parentSchema.required is not None and name in parentSchema.required
    import_model = reference.ref.split("/")[-1]
    return Property(
        name=name,
        type=import_model if required else f"Optional[{import_model}]",
        required=required,
        default=None if required else "None"), import_model


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
                content=JINJA_ENV.get_template(ENUM_TEMPLATE).render(name=name,**schema.dict()),
                openapi_object=schema,
                references=[],
                properties=[],
            )
            try:
                compile(m.content, "<string>", "exec")
                models.append(m)
            except SyntaxError as e: #pragma: no cover
                typer.echo(f"Error in model {name}: {e}")

            continue  #pragma: no cover

        import_models = []
        properties = []
        for prop_name, property in schema.properties.items():
            if isinstance(property, Reference):
                conv_property, import_model = _generate_property_from_reference(prop_name, property, schema)
                import_models.append(import_model)
            else:
                conv_property = _generate_property_from_schema(prop_name, property, schema)
            properties.append(conv_property)

        generated_content = JINJA_ENV.get_template(MODELS_TEMPLATE).render(
            schema_name=name,
            schema=schema,
            properties=properties,
            import_models=import_models,
        )

        try:
            compile(generated_content, "<string>", "exec")
        except SyntaxError as e: #pragma: no cover
            typer.echo(f"Error in model {name}: {e}") #pragma: no cover

        models.append(Model(
            file_name=name,
            content=generated_content,
            openapi_object=schema,
            references=import_models,
            properties=properties,
        ))

    return models

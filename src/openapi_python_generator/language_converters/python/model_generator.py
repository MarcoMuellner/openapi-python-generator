from typing import List, Optional, Union

import click
from openapi_pydantic.v3.v3_0 import (
    Components as Components30,
)
from openapi_pydantic.v3.v3_0 import (
    Reference as Reference30,
)
from openapi_pydantic.v3.v3_0 import (
    Schema as Schema30,
)
from openapi_pydantic.v3.v3_1 import (
    Components as Components31,
)
from openapi_pydantic.v3.v3_1 import (
    Reference as Reference31,
)
from openapi_pydantic.v3.v3_1 import (
    Schema as Schema31,
)

from openapi_python_generator.common import PydanticVersion
from openapi_python_generator.language_converters.python import common
from openapi_python_generator.language_converters.python.jinja_config import (
    ENUM_TEMPLATE,
    MODELS_TEMPLATE,
    MODELS_TEMPLATE_PYDANTIC_V2,
    create_jinja_env,
)
from openapi_python_generator.models import Model, Property, TypeConversion

# Type aliases for compatibility
Schema = Union[Schema30, Schema31]
Reference = Union[Reference30, Reference31]
Components = Union[Components30, Components31]


def _normalize_schema_type(schema: Schema) -> Optional[str]:
    """
    Normalize schema.type to a consistent string representation.

    Handles:
    - DataType enum (e.g., DataType.STRING)
    - String values (e.g., "string")
    - List of types (takes first element)
    - None (returns None)

    :param schema: Schema object
    :return: Normalized type string or None
    """
    if schema.type is None:
        return None

    # Handle list of types (take first)
    if isinstance(schema.type, list):
        if len(schema.type) == 0:
            return None
        first_type = schema.type[0]
        if hasattr(first_type, "value"):
            return first_type.value
        return str(first_type)

    # Handle DataType enum
    if hasattr(schema.type, "value"):
        return schema.type.value

    # Handle string
    return str(schema.type)


def _is_type(schema: Schema, type_name: str) -> bool:
    """
    Check if schema represents a specific type.

    Handles all forms: DataType.STRING, "string", "DataType.STRING", ["string", ...]

    :param schema: Schema object
    :param type_name: Type name to check (e.g., "string", "integer")
    :return: True if schema matches type_name
    """
    normalized = _normalize_schema_type(schema)
    return normalized == type_name


def _handle_format_conversions(
    schema: Schema, base_type: str, required: bool
) -> Optional[TypeConversion]:
    """
    Handle UUID and datetime format conversions based on orjson usage.

    Returns TypeConversion if special format handling is needed, None otherwise.

    :param schema: Schema object
    :param base_type: Base type string (e.g., "string")
    :param required: Whether the field is required
    :return: TypeConversion or None
    """
    if base_type != "string" or schema.schema_format is None:
        return None

    # Handle UUID formats
    if schema.schema_format.startswith("uuid") and common.get_use_orjson():
        if len(schema.schema_format) > 4 and schema.schema_format[4].isnumeric():
            uuid_type = schema.schema_format.upper()
            converted_type = uuid_type if required else f"Optional[{uuid_type}]"
            return TypeConversion(
                original_type=base_type,
                converted_type=converted_type,
                import_types=[f"from pydantic import {uuid_type}"],
            )
        else:
            converted_type = "UUID" if required else "Optional[UUID]"
            return TypeConversion(
                original_type=base_type,
                converted_type=converted_type,
                import_types=["from uuid import UUID"],
            )

    # Handle datetime format
    if schema.schema_format == "date-time" and common.get_use_orjson():
        converted_type = "datetime" if required else "Optional[datetime]"
        return TypeConversion(
            original_type=base_type,
            converted_type=converted_type,
            import_types=["from datetime import datetime"],
        )

    return None


def _wrap_optional(type_str: str, required: bool) -> str:
    """
    Add Optional[] wrapper if not required.

    :param type_str: Type string to potentially wrap
    :param required: Whether the field is required
    :return: Wrapped or unwrapped type string
    """
    if required:
        return type_str
    return f"Optional[{type_str}]"


def _collect_unique_imports(conversions: List[TypeConversion]) -> Optional[List[str]]:
    """
    Safely collect and deduplicate imports from conversions.

    :param conversions: List of TypeConversion objects
    :return: Ordered unique list of import statements, or None if empty
    """
    imports = []
    seen = set()

    for conversion in conversions:
        if conversion.import_types is not None:
            for import_stmt in conversion.import_types:
                if import_stmt not in seen:
                    imports.append(import_stmt)
                    seen.add(import_stmt)

    return imports if imports else None


def _convert_primitive_type(type_str: Optional[str], required: bool) -> TypeConversion:
    """
    Handle simple primitive type conversion (string, int, float, bool, object, null, Any).

    :param type_str: Normalized type string (can be None for schemas without a type)
    :param required: Whether the field is required
    :return: TypeConversion for the primitive type
    """
    type_map = {
        "string": "str",
        "integer": "int",
        "number": "float",
        "boolean": "bool",
        "object": "Dict[str, Any]",
        "null": "None",
    }

    python_type = type_map.get(type_str, "str")  # Default to str for unknown types
    if type_str is None:
        python_type = "Any"

    converted_type = _wrap_optional(python_type, required)

    return TypeConversion(
        original_type=type_str if type_str else "object",
        converted_type=converted_type,
        import_types=None,
    )


def _convert_array_type(
    schema: Schema, required: bool, model_name: Optional[str]
) -> TypeConversion:
    """
    Handle array type conversion.

    :param schema: Schema object with type="array"
    :param required: Whether the field is required (for the array itself)
    :param model_name: Name of the model being generated
    :return: TypeConversion for the array type
    """
    import_types: Optional[List[str]] = None

    # Build the List[...] wrapper
    if required:
        list_prefix = "List["
        list_suffix = "]"
    else:
        list_prefix = "Optional[List["
        list_suffix = "]]"

    # Handle array items
    if isinstance(schema.items, Reference30) or isinstance(schema.items, Reference31):
        # For reference items, pass the array's required status to force_required
        # This makes items Optional when array is optional: Optional[List[Optional[Type]]]
        converted_reference = _generate_property_from_reference(
            model_name or "", "", schema.items, schema, required
        )
        import_types = converted_reference.type.import_types
        original_type = "array<" + converted_reference.type.original_type + ">"
        converted_type = (
            list_prefix + converted_reference.type.converted_type + list_suffix
        )
    elif isinstance(schema.items, Schema30) or isinstance(schema.items, Schema31):
        # For schema items, always pass True (items are always required within the array)
        item_type_str = _normalize_schema_type(schema.items)
        original_type = "array<" + (item_type_str if item_type_str else "unknown") + ">"
        item_conversion = type_converter(schema.items, True, model_name)
        converted_type = list_prefix + item_conversion.converted_type + list_suffix
        import_types = item_conversion.import_types
    else:
        original_type = "array<unknown>"
        converted_type = list_prefix + "Any" + list_suffix

    return TypeConversion(
        original_type=original_type,
        converted_type=converted_type,
        import_types=import_types,
    )


def _convert_composite_schema(
    kind: str,
    sub_schemas: List[Union[Schema, Reference]],
    required: bool,
    model_name: Optional[str],
) -> TypeConversion:
    """
    Handle allOf/oneOf/anyOf composition.

    :param kind: "allOf", "oneOf", or "anyOf"
    :param sub_schemas: List of schemas or references to compose
    :param required: Whether the field is required
    :param model_name: Name of the model being generated (for self-references)
    :return: TypeConversion for the composite type
    """
    conversions = []

    for sub_schema in sub_schemas:
        if isinstance(sub_schema, Schema30) or isinstance(sub_schema, Schema31):
            conversions.append(type_converter(sub_schema, True, model_name))
        else:
            # Reference
            import_type = common.normalize_symbol(sub_schema.ref.split("/")[-1])

            # Handle self-reference
            if import_type == model_name and model_name is not None:
                conversions.append(
                    TypeConversion(
                        original_type=sub_schema.ref,
                        converted_type=f'"{model_name}"',
                        import_types=None,
                    )
                )
            else:
                conversions.append(
                    TypeConversion(
                        original_type=sub_schema.ref,
                        converted_type=import_type,
                        import_types=[f"from .{import_type} import {import_type}"],
                    )
                )

    # Build original type string
    if kind == "allOf":
        original_type = (
            "tuple<" + ",".join([c.original_type for c in conversions]) + ">"
        )
        type_wrapper = "Tuple"
    else:  # oneOf or anyOf
        original_type = (
            "union<" + ",".join([c.original_type for c in conversions]) + ">"
        )
        type_wrapper = "Union"

    # Build converted type string
    if len(conversions) == 1:
        converted_type = conversions[0].converted_type
    else:
        converted_type = (
            type_wrapper + "[" + ",".join([c.converted_type for c in conversions]) + "]"
        )

    converted_type = _wrap_optional(converted_type, required)
    import_types = _collect_unique_imports(conversions)

    return TypeConversion(
        original_type=original_type,
        converted_type=converted_type,
        import_types=import_types,
    )


def type_converter(
    schema: Union[Schema, Reference],
    required: bool = False,
    model_name: Optional[str] = None,
) -> TypeConversion:
    """
    Converts an OpenAPI type to a Python type.

    :param schema: Schema or Reference containing the type to be converted
    :param model_name: Name of the original model on which the type is defined
    :param required: Flag indicating if the type is required by the class
    :return: The converted type
    """
    # Handle Reference objects by converting them to type references
    if isinstance(schema, Reference30) or isinstance(schema, Reference31):
        import_type = common.normalize_symbol(schema.ref.split("/")[-1])
        converted_type = _wrap_optional(import_type, required)

        return TypeConversion(
            original_type=schema.ref,
            converted_type=converted_type,
            import_types=(
                [f"from .{import_type} import {import_type}"]
                if import_type != model_name
                else None
            ),
        )

    # Handle composite schemas (allOf/oneOf/anyOf)
    if schema.allOf is not None:
        return _convert_composite_schema("allOf", schema.allOf, required, model_name)

    if schema.oneOf is not None:
        return _convert_composite_schema("oneOf", schema.oneOf, required, model_name)

    if schema.anyOf is not None:
        return _convert_composite_schema("anyOf", schema.anyOf, required, model_name)

    # Get normalized type string
    type_str = _normalize_schema_type(schema)
    original_type = type_str if type_str is not None else "object"

    # Check for format conversions (UUID, datetime)
    format_conversion = _handle_format_conversions(schema, original_type, required)
    if format_conversion is not None:
        return format_conversion

    # Handle array type (special case with items)
    if _is_type(schema, "array"):
        return _convert_array_type(schema, required, model_name)

    # Handle all other primitive types
    return _convert_primitive_type(type_str, required)


def _generate_property_from_schema(
    model_name: str, name: str, schema: Schema, parent_schema: Optional[Schema] = None
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

    import_type = None
    if required:
        import_type = [] if name == model_name else [name]

    return Property(
        name=name,
        type=type_converter(schema, required, model_name),
        required=required,
        default=None if required else "None",
        import_type=import_type,
    )


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


def generate_models(
    components: Components, pydantic_version: PydanticVersion = PydanticVersion.V2
) -> List[Model]:
    """
    Receives components from an OpenAPI 3.0+ specification and generates the models from it.
    It does so, by iterating over the components.schemas dictionary. For each schema, it checks if
    it is a normal schema (i.e. simple type like string, integer, etc.), a reference to another schema, or
    an array of types/references. It then computes pydantic models from it using jinja2
    :param components: The components from an OpenAPI 3.0+ specification.
    :param pydantic_version: The version of pydantic to use.
    :return: A list of models.
    """
    models: List[Model] = []

    if components.schemas is None:
        return models

    jinja_env = create_jinja_env()
    for schema_name, schema_or_reference in components.schemas.items():
        name = common.normalize_symbol(schema_name)
        if schema_or_reference.enum is not None:
            value_dict = schema_or_reference.model_dump()
            value_dict["enum"] = [
                (common.normalize_symbol(str(i)).upper(), i) for i in value_dict["enum"]
            ]
            m = Model(
                file_name=name,
                content=jinja_env.get_template(ENUM_TEMPLATE).render(
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
            if isinstance(property, Reference30) or isinstance(property, Reference31):
                conv_property = _generate_property_from_reference(
                    name, prop_name, property, schema_or_reference
                )
            else:
                conv_property = _generate_property_from_schema(
                    name, prop_name, property, schema_or_reference
                )
            properties.append(conv_property)

        template_name = (
            MODELS_TEMPLATE_PYDANTIC_V2
            if pydantic_version == PydanticVersion.V2
            else MODELS_TEMPLATE
        )

        generated_content = jinja_env.get_template(template_name).render(
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

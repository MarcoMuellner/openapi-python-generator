import re
import traceback
from typing import Dict, List
from caseconverter import pascalcase, snakecase

import click

import openapi_python_generator
from openapi_python_generator.language_converters.python.service_generator import (
    HTTP_OPERATIONS,
)
from openapi_python_generator.language_converters.python.utils import (
    _generate_property_from_reference,
    _generate_property_from_schema,
)

if openapi_python_generator.OPENAPI_VERSION is None:
    raise ValueError("OPENAPI_VERSION must be set")

from openapi_python_generator.language_converters.python import common
from openapi_python_generator.language_converters.python.jinja_config import (
    ENUM_TEMPLATE,
)
from openapi_python_generator.language_converters.python.jinja_config import (
    MODELS_TEMPLATE,
)
from openapi_python_generator.language_converters.python.jinja_config import (
    create_jinja_env,
)
from openapi_python_generator.models import Model

if openapi_python_generator.OPENAPI_VERSION == "3.0":
    from openapi_pydantic.v3.v3_0_3.components import Components
    from openapi_pydantic.v3.v3_0_3.reference import Reference
    from openapi_pydantic.v3.v3_0_3.path_item import PathItem
    from openapi_pydantic.v3.v3_0_3.operation import Operation
    from openapi_pydantic.v3.v3_0_3.response import Response
    from openapi_pydantic.v3.v3_0_3.schema import Schema
else:
    from openapi_pydantic import Components
    from openapi_pydantic import Reference
    from openapi_pydantic import PathItem
    from openapi_pydantic import Operation
    from openapi_pydantic import Response
    from openapi_pydantic import Schema


def generate_models(
    components: Components,
    paths: Dict[str, PathItem],
) -> List[Model]:
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

    jinja_env = create_jinja_env()
    for schema_name, schema_or_reference in components.schemas.items():
        name = common.normalize_symbol(schema_name)
        name = pascalcase(name)
        if schema_or_reference.enum is not None:
            value_dict = schema_or_reference.dict()
            regex = re.compile(r"[\s\/=\*\+]+")
            value_dict["enum"] = [
                (re.sub(regex, "_", i) if isinstance(i, str) else f"value_{i}", i)
                for i in value_dict["enum"]
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
                click.echo(f"Error in model {name}: {traceback.format_exc()}")

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

        generated_content = jinja_env.get_template(MODELS_TEMPLATE).render(
            schema_name=name, schema=schema_or_reference, properties=properties
        )

        try:
            compile(generated_content, "<string>", "exec")
        except SyntaxError as e:  # pragma: no cover
            click.echo(
                f"Error in model {name}: {traceback.format_exc()}"
            )  # pragma: no cover

        models.append(
            Model(
                file_name=name,
                content=generated_content,
                openapi_object=schema_or_reference,
                properties=properties,
            )
        )

    if components.responses is not None:
        for response_name, response in components.responses.items():
            name = pascalcase(response_name)
            if response.content is None:
                models.append(
                    Model(
                        file_name=name,
                        content=f"from pydantic import BaseModel\n\nclass {name}(BaseModel):\n    pass",
                        openapi_object=Schema(),
                        properties=[],
                    )
                )
                continue
            if "application/json" not in response.content:
                continue
            media_type = response.content["application/json"]

            if media_type.media_type_schema is None:
                continue

            if isinstance(media_type.media_type_schema, Reference):
                ref_name = media_type.media_type_schema.ref.split("/")[-1]
                ref_model_name = snakecase(ref_name)
                models.append(
                    Model(
                        file_name=name,
                        content=f"from .{ref_model_name} import {ref_model_name}\n\nclass {name}({ref_model_name}):\n    pass",
                        openapi_object=Schema(),
                        properties=[],
                    )
                )
                continue

            properties = []
            property_iterator = (
                media_type.media_type_schema.properties.items()
                if media_type.media_type_schema.properties is not None
                else {}
            )
            for prop_name, property in property_iterator:
                if isinstance(property, Reference):
                    conv_property = _generate_property_from_reference(
                        name, prop_name, property, media_type.media_type_schema
                    )
                else:
                    conv_property = _generate_property_from_schema(
                        name, prop_name, property, media_type.media_type_schema
                    )
                properties.append(conv_property)

            generated_content = jinja_env.get_template(MODELS_TEMPLATE).render(
                schema_name=name,
                schema=media_type.media_type_schema,
                properties=properties,
            )

            try:
                compile(generated_content, "<string>", "exec")
            except SyntaxError as e:  # pragma: no cover
                click.echo(
                    f"Error in model {name}: {traceback.format_exc()}"
                )  # pragma: no cover

            models.append(
                Model(
                    file_name=name,
                    content=generated_content,
                    openapi_object=media_type.media_type_schema,
                    properties=properties,
                )
            )

    if components.requestBodies is not None:
        for body_name, body in components.requestBodies.items():
            if body.content is None:
                continue
            if "application/json" not in body.content:
                continue
            media_type = body.content["application/json"]

            if media_type.media_type_schema is None:
                continue

            if not isinstance(media_type.media_type_schema, Schema):
                continue

            name = pascalcase(body_name)

            properties = []
            property_iterator = (
                media_type.media_type_schema.properties.items()
                if media_type.media_type_schema.properties is not None
                else {}
            )
            for prop_name, property in property_iterator:
                if isinstance(property, Reference):
                    conv_property = _generate_property_from_reference(
                        name, prop_name, property, media_type.media_type_schema
                    )
                else:
                    conv_property = _generate_property_from_schema(
                        name, prop_name, property, media_type.media_type_schema
                    )
                properties.append(conv_property)

            generated_content = jinja_env.get_template(MODELS_TEMPLATE).render(
                schema_name=name,
                schema=media_type.media_type_schema,
                properties=properties,
            )

            try:
                compile(generated_content, "<string>", "exec")
            except SyntaxError as e:  # pragma: no cover
                click.echo(f"Error in model {name}: {traceback.format_exc()}")

            models.append(
                Model(
                    file_name=name,
                    content=generated_content,
                    openapi_object=media_type.media_type_schema,
                    properties=properties,
                )
            )

    for path_name, path in paths.items():
        for http_operation in HTTP_OPERATIONS:
            op: Operation = path.__getattribute__(http_operation)
            if op is None:
                continue

            for status, response in op.responses.items():
                if not status.startswith("2"):
                    continue
                if not isinstance(response, Response):
                    continue
                if response.content is None:
                    continue
                if "application/json" not in response.content:
                    continue
                media_type = response.content["application/json"]

                if media_type.media_type_schema is None:
                    continue

                if not isinstance(media_type.media_type_schema, Schema):
                    continue

                name = f"{pascalcase(path_name.replace('/', '_'))}{http_operation.capitalize()}Response"

                properties = []
                property_iterator = (
                    media_type.media_type_schema.properties.items()
                    if media_type.media_type_schema.properties is not None
                    else {}
                )
                for prop_name, property in property_iterator:
                    if isinstance(property, Reference):
                        conv_property = _generate_property_from_reference(
                            name, prop_name, property, media_type.media_type_schema
                        )
                    else:
                        conv_property = _generate_property_from_schema(
                            name, prop_name, property, media_type.media_type_schema
                        )
                    properties.append(conv_property)

                generated_content = jinja_env.get_template(MODELS_TEMPLATE).render(
                    schema_name=name,
                    schema=media_type.media_type_schema,
                    properties=properties,
                )

                try:
                    compile(generated_content, "<string>", "exec")
                except SyntaxError as e:  # pragma: no cover
                    click.echo(
                        f"Error in model {name}: {traceback.format_exc()}"
                    )  # pragma: no cover

                models.append(
                    Model(
                        file_name=name,
                        content=generated_content,
                        openapi_object=media_type.media_type_schema,
                        properties=properties,
                    )
                )

    return models

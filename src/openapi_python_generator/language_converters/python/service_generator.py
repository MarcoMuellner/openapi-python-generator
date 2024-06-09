import re
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Tuple
from typing import Union
from deep_translator import GoogleTranslator
from caseconverter import snakecase
from caseconverter import pascalcase

import click
from openapi_pydantic import DataType
import openapi_python_generator
from openapi_python_generator.language_converters.python.utils import type_converter

if openapi_python_generator.OPENAPI_VERSION == "3.0":
    from openapi_pydantic.v3.v3_0_3.media_type import MediaType
    from openapi_pydantic.v3.v3_0_3.operation import Operation
    from openapi_pydantic.v3.v3_0_3.parameter import Parameter
    from openapi_pydantic.v3.v3_0_3.path_item import PathItem
    from openapi_pydantic.v3.v3_0_3.reference import Reference
    from openapi_pydantic.v3.v3_0_3.request_body import RequestBody
    from openapi_pydantic.v3.v3_0_3.response import Response
    from openapi_pydantic.v3.v3_0_3.schema import Schema
    from openapi_pydantic.v3.v3_0_3.components import Components
else:
    from openapi_pydantic import MediaType
    from openapi_pydantic import Operation
    from openapi_pydantic import Parameter
    from openapi_pydantic import PathItem
    from openapi_pydantic import Reference
    from openapi_pydantic import RequestBody
    from openapi_pydantic import Response
    from openapi_pydantic import Schema
    from openapi_pydantic import Components

from openapi_python_generator.language_converters.python import common
from openapi_python_generator.language_converters.python.common import normalize_symbol
from openapi_python_generator.language_converters.python.jinja_config import (
    create_jinja_env,
)
from openapi_python_generator.common import LibraryConfig
from openapi_python_generator.models import OpReturnType
from openapi_python_generator.models import Service
from openapi_python_generator.models import ServiceOperation
from openapi_python_generator.models import TypeConversion


HTTP_OPERATIONS = ["get", "post", "put", "delete", "options", "head", "patch", "trace"]


def generate_body_param(operation: Operation) -> Union[str, None]:
    if operation.requestBody is None:
        return None
    else:
        if isinstance(operation.requestBody, Reference):
            return "data.dict()"

        if operation.requestBody.content is None:
            return None  # pragma: no cover

        if operation.requestBody.content.get("application/json") is None:
            return None  # pragma: no cover

        media_type = operation.requestBody.content.get("application/json")

        if media_type is None:
            return None  # pragma: no cover

        if isinstance(media_type.media_type_schema, Reference):
            return "data.dict()"
        elif isinstance(media_type.media_type_schema, Schema):
            schema = media_type.media_type_schema
            if schema.type == "array":
                return "[i.dict() for i in data]"
            elif schema.type == "object":
                return "data"
            elif schema.type is None and schema.oneOf is not None:
                return "data.dict()"
            else:
                raise Exception(
                    f"Unsupported schema type for request body: {schema.type}"
                )  # pragma: no cover
        else:
            raise Exception(
                f"Unsupported schema type for request body: {type(media_type.media_type_schema)}"
            )  # pragma: no cover


def generate_params(
    operation: Operation,
    components: Components,
) -> str:
    def _generate_params_from_content(content: Union[Reference, Schema]):
        if isinstance(content, Reference):
            type_name = content.ref.split("/")[-1]
            type_name = pascalcase(type_name)
            return f"data : {type_name}"
        else:
            return f"data : {type_converter(content, True).converted_type}"

    if operation.parameters is None and operation.requestBody is None:
        return ""

    params = ""
    default_params = ""
    if operation.parameters is not None:
        for param in operation.parameters:
            if not isinstance(param, Parameter) and not isinstance(param, Reference):
                raise NotImplementedError(f"Unsupported parameter type: {type(param)}")

            if isinstance(param, Reference):
                ref = param.ref.split("/")[-1]
                param = components.parameters.get(ref)
                if param is None:
                    raise Exception(f"Unable to find parameter {ref}")

            converted_result = ""
            required = False
            param_name_cleaned = common.normalize_symbol(param.name)

            if isinstance(param.param_schema, Schema):
                converted_result = (
                    f"{param_name_cleaned} : {type_converter(param.param_schema, param.required).converted_type}"
                    + ("" if param.required else " = None")
                )
                required = param.required
            elif isinstance(param.param_schema, Reference):
                converted_result = (
                    f"{param_name_cleaned} : {param.param_schema.ref.split('/')[-1] }"
                    + (
                        ""
                        if isinstance(param, Reference) or param.required
                        else " = None"
                    )
                )
                required = isinstance(param, Reference) or param.required

            if required:
                params += f"{converted_result}, "
            else:
                default_params += f"{converted_result}, "

    operation_request_body_types = [
        "application/json",
        "text/plain",
        "multipart/form-data",
    ]

    if operation.requestBody is not None:
        if (
            isinstance(operation.requestBody, RequestBody)
            and isinstance(operation.requestBody.content, dict)
            and any(
                [
                    operation.requestBody.content.get(i) is not None
                    for i in operation_request_body_types
                ]
            )
        ):
            get_keyword = [
                i
                for i in operation_request_body_types
                if operation.requestBody.content.get(i) is not None
            ][0]
            content = operation.requestBody.content.get(get_keyword)
            if content is not None and (
                isinstance(content.media_type_schema, Schema)
                or isinstance(content.media_type_schema, Reference)
            ):
                params += (
                    f"{_generate_params_from_content(content.media_type_schema)}, "
                )
            else:
                raise Exception(
                    f"Unsupported media type schema for {str(operation)}"
                )  # pragma: no cover
        elif isinstance(operation.requestBody, Reference):
            params += f"data : {operation.requestBody.ref.split('/')[-1]}, "
        else:
            raise Exception(
                f"Unsupported request body type: {type(operation.requestBody)}"
            )
    # Replace - with _ in params
    params = params.replace("-", "_")
    default_params = default_params.replace("-", "_")

    return params + default_params


def generate_operation_id(
    operation: Operation, http_op: str, path_name: Optional[str] = None
) -> str:
    if operation.operationId is not None:
        return common.normalize_symbol(operation.operationId)
    elif path_name is not None:
        return common.normalize_symbol(f"{http_op}_{path_name}")
    else:
        raise Exception(
            f"OperationId is not defined for {http_op} of path_name {path_name} --> {operation.summary}"
        )  # pragma: no cover


def _generate_params(
    operation: Operation,
    components: Components,
    param_in: Literal["query", "header"] = "query",
):
    if operation.parameters is None:
        return []

    params = []
    for param in operation.parameters:
        if isinstance(param, Reference):
            ref = param.ref.split("/")[-1]
            param = components.parameters.get(ref)
            if param is None:
                raise Exception(f"Unable to find parameter {ref}")

        if isinstance(param, Parameter) and param.param_in == param_in:
            param_name_cleaned = common.normalize_symbol(param.name)
            params.append(f"{param.name!r} : {param_name_cleaned}")

    return params


def generate_query_params(
    operation: Operation,
    components: Components,
) -> List[str]:
    return _generate_params(operation, components, "query")


def generate_header_params(
    operation: Operation,
    components: Components,
) -> List[str]:
    return _generate_params(operation, components, "header")


def generate_return_type(
    operation: Operation, http_opertaion: str, path_name: str
) -> OpReturnType:
    if operation.responses is None:
        return OpReturnType(type=None, status_code=200, complex_type=False)

    good_responses: List[Tuple[int, Union[Response, Reference]]] = [
        (int(status_code), response)
        for status_code, response in operation.responses.items()
        if status_code.startswith("2")
    ]
    if len(good_responses) == 0:
        return OpReturnType(type=None, status_code=200, complex_type=False)

    chosen_response = good_responses[0][1]

    if isinstance(chosen_response, Response) and chosen_response.content is not None:
        media_type_schema = chosen_response.content.get("application/json")
    elif isinstance(chosen_response, Reference):
        media_type_schema = MediaType(
            media_type_schema=chosen_response
        )  # pragma: no cover
    else:
        return OpReturnType(
            type=None, status_code=good_responses[0][0], complex_type=False
        )

    if isinstance(media_type_schema, MediaType):
        if isinstance(media_type_schema.media_type_schema, Reference):
            response_model_name = media_type_schema.media_type_schema.ref.split("/")[-1]
            response_model_name = pascalcase(response_model_name)
            type_conv = TypeConversion(
                original_type=media_type_schema.media_type_schema.ref,
                converted_type=response_model_name,
                import_types=[response_model_name],
            )
            return OpReturnType(
                type=type_conv,
                status_code=good_responses[0][0],
                complex_type=True,
            )
        elif isinstance(media_type_schema.media_type_schema, Schema):
            if media_type_schema.media_type_schema.type == DataType.OBJECT:
                response_model_name = f"{pascalcase(path_name.replace('/', '_'))}{http_opertaion.capitalize()}Response"
                type_conv = TypeConversion(
                    original_type=response_model_name,
                    converted_type=response_model_name,
                    import_types=[response_model_name],
                )
                return OpReturnType(
                    type=type_conv,
                    status_code=good_responses[0][0],
                    complex_type=True,
                )
            else:
                converted_result = type_converter(
                    media_type_schema.media_type_schema,
                    True,
                )
                if "array" in converted_result.original_type and isinstance(
                    converted_result.import_types, list
                ):
                    matched = re.findall(
                        r"List\[(.+)\]", converted_result.converted_type
                    )
                    if len(matched) > 0:
                        list_type = matched[0]
                    else:
                        raise Exception(
                            f"Unable to parse list type from {converted_result.converted_type}"
                        )  # pragma: no cover
                else:
                    list_type = None
                return OpReturnType(
                    type=converted_result,
                    status_code=good_responses[0][0],
                    complex_type=converted_result.import_types is not None
                    and len(converted_result.import_types) > 0,
                    list_type=list_type,
                )
        else:
            raise Exception("Unknown media type schema type")  # pragma: no cover
    elif media_type_schema is None:
        return OpReturnType(
            type=None,
            status_code=good_responses[0][0],
            complex_type=False,
        )
    else:
        raise Exception("Unknown media type schema type")  # pragma: no cover


def generate_services(
    paths: Dict[str, PathItem],
    components: Components,
    library_config: LibraryConfig,
) -> List[Service]:
    """
    Generates services from a paths object.
    :param paths: paths object to be converted
    :return: List of services
    """
    jinja_env = create_jinja_env()

    def generate_service_operation(
        op: Operation,
        path_name: str,
        async_type: bool,
    ) -> ServiceOperation:
        params = generate_params(op, components)
        operation_id = generate_operation_id(op, http_operation, path_name)
        query_params = generate_query_params(op, components)
        header_params = generate_header_params(op, components)
        return_type = generate_return_type(op, http_operation, path_name)
        body_param = generate_body_param(op)

        so = ServiceOperation(
            params=params,
            operation_id=operation_id,
            query_params=query_params,
            header_params=header_params,
            return_type=return_type,
            operation=op,
            pathItem=path,
            content="",
            async_client=async_type,
            body_param=body_param,
            path_name=path_name,
            method=http_operation,
            use_orjson=common.get_use_orjson(),
        )

        so.content = jinja_env.get_template(library_config.template_name).render(
            **so.dict()
        )

        if op.tags is not None and len(op.tags) > 0:
            tag = op.tags[0]
            if tag is not None:
                tag = GoogleTranslator(source="auto", target="en").translate(tag)
                tag = snakecase(tag)
                so.tag = normalize_symbol(tag)

        try:
            compile(so.content, "<string>", "exec")
        except SyntaxError as e:  # pragma: no cover
            click.echo(f"Error in service {so.operation_id}: {e}")  # pragma: no cover

        return so

    services = []
    service_ops = []
    for path_name, path in paths.items():
        for http_operation in HTTP_OPERATIONS:
            op = path.__getattribute__(http_operation)
            if op is None:
                continue

            if library_config.include_sync:
                sync_so = generate_service_operation(op, path_name, False)
                service_ops.append(sync_so)

            if library_config.include_async:
                async_so = generate_service_operation(op, path_name, True)
                service_ops.append(async_so)

    tags = set([so.tag for so in service_ops])

    for tag in tags:
        services.append(
            Service(
                file_name=f"{tag}_service",
                operations=[
                    so for so in service_ops if so.tag == tag and not so.async_client
                ],
                content="\n".join(
                    [
                        so.content
                        for so in service_ops
                        if so.tag == tag and not so.async_client
                    ]
                ),
                async_client=False,
                library_import=library_config.library_name,
                use_orjson=common.get_use_orjson(),
            )
        )

    for tag in tags:
        services.append(
            Service(
                file_name=f"async_{tag + '_' if tag else ''}service",
                operations=[
                    so for so in service_ops if so.tag == tag and so.async_client
                ],
                content="\n".join(
                    [
                        so.content
                        for so in service_ops
                        if so.tag == tag and so.async_client
                    ]
                ),
                async_client=True,
                library_import=library_config.library_name,
                use_orjson=common.get_use_orjson(),
            )
        )

    return services

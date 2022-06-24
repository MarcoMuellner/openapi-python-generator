import itertools
from typing import Dict, List, Tuple, Union

import typer
from openapi_schema_pydantic import PathItem, Operation, Response, MediaType, Reference, Schema

from openapi_python_generator.language_converters.python.jinja_config import JINJA_ENV, HTTPX_TEMPLATE
from openapi_python_generator.language_converters.python.model_generator import type_converter
from openapi_python_generator.models import Service, ServiceOperation, OpReturnType

HTTP_OPERATIONS = ["get", "post", "put", "delete", "options", "head", "patch", "trace"]


def generate_body_param(operation: Operation) -> Union[str, None]:
    if operation.requestBody is None:
        return None
    else:
        return "data"


def generate_params(operation: Operation) -> List[str]:
    def _generate_params_from_content(content: Union[Reference, Schema]):
        if isinstance(content, Reference):
            return f"data : {content.ref.split('/')[-1]}"
        elif isinstance(content, Schema):
            return f"data : {type_converter(content, True)}"
        else:
            raise Exception("Unknown content type")

    if operation.parameters is None and operation.requestBody is None:
        return []

    params = []
    if operation.parameters is not None:
        for param in operation.parameters:
            if isinstance(param.param_schema, Schema):
                params.append(f"{param.name} : {type_converter(param.param_schema, param.required)}" + (
                    "" if param.required else " = None"))
            elif isinstance(param.param_schema, Reference):
                params.append(
                    f"{param.name} : {param.param_schema.ref.split('/')[-1]}" + ("" if param.required else " = None"))
            else:
                raise Exception("Unknown param schema type")

    if operation.requestBody is not None:
        if isinstance(operation.requestBody.content, MediaType):
            params.append(_generate_params_from_content(operation.requestBody.content.media_type_schema))
        elif isinstance(operation.requestBody.content,
                        dict) and 'application/json' in operation.requestBody.content.keys():
            params.append(
                _generate_params_from_content(operation.requestBody.content['application/json'].media_type_schema))
        else:
            raise Exception("Unknown media type schema type")

    return params


def generate_operation_id(operation: Operation, http_op: str) -> str:
    return f"{http_op.lower()}_{operation.operationId.replace('-', '_')}"


def generate_query_params(operation: Operation) -> List[str]:
    if operation.parameters is None:
        return []

    params = []
    for param in operation.parameters:
        if param.param_in == "query":
            params.append(f"'{param.name}' : {param.name}")

    return params


def generate_return_type(operation: Operation) -> OpReturnType:
    if operation.responses is None:
        return OpReturnType(
            type="None",
            status_code="200",
            complex_type="False"
        )
    good_responses: List[Tuple[int, Response]] = [(int(status_code), response) for status_code, response in
                                                  operation.responses.items() if status_code.startswith('2')]
    if len(good_responses) == 0:
        return OpReturnType(
            type="None",
            status_code="200",
            complex_type="False"
        )

    media_type_schema = good_responses[0][1].content.get('application/json')

    if isinstance(media_type_schema, MediaType):
        try:
            if isinstance(media_type_schema.media_type_schema, Reference):
                return OpReturnType(
                    type=media_type_schema.media_type_schema.ref.split("/")[-1],
                    status_code=good_responses[0][0],
                    complex_type=True
                )
            elif isinstance(media_type_schema.media_type_schema, Schema):
                return OpReturnType(
                    type=type_converter(media_type_schema.media_type_schema, True),
                    status_code=good_responses[0][0],
                    complex_type=False
                )
            else:
                raise Exception("Unknown media type schema type")
        except TypeError as e:
            print(e)
            return OpReturnType(
                type="Dict",
                status_code=good_responses[0][0],
                complex_type=False
            )
    else:
        raise Exception("Unknown media type schema type")


def generate_services(paths: Dict[str, PathItem]) -> List[Service]:
    """
    Generates services from a paths object.
    :param paths: paths object to be converted
    :return: List of services
    """
    services = []
    service_ops = []
    for path_name, path in paths.items():
        for http_operation in HTTP_OPERATIONS:
            op = path.__getattribute__(http_operation)
            if op is None:
                continue

            params = generate_params(op)
            operation_id = generate_operation_id(op, http_operation)
            query_params = generate_query_params(op)
            return_type = generate_return_type(op)
            body_param = generate_body_param(op)

            sync_so = ServiceOperation(
                params=params,
                operation_id=operation_id,
                query_params=query_params,
                return_type=return_type,
                operation=op,
                pathItem=path,
                content="",
                async_client=False,
                body_param=body_param,
                path_name=path_name
            )

            async_so = ServiceOperation(
                params=params,
                operation_id=operation_id,
                query_params=query_params,
                return_type=return_type,
                operation=op,
                pathItem=path,
                content="",
                async_client=True,
                body_param=body_param,
                path_name=path_name
            )

            sync_so.content = JINJA_ENV.get_template(HTTPX_TEMPLATE).render(**sync_so.dict())
            async_so.content = JINJA_ENV.get_template(HTTPX_TEMPLATE).render(**async_so.dict())

            if op.tags is not None and len(op.tags) > 0:
                sync_so.tag = op.tags[0]
                async_so.tag = op.tags[0]

            service_ops.append(sync_so)
            service_ops.append(async_so)

            try:
                compile(sync_so.content, "<string>", "exec")
            except SyntaxError as e:
                typer.echo(f"Error in service {sync_so.operation_id}: {e}")
                typer.Exit()

            try:
                compile(async_so.content, "<string>", "exec")
            except SyntaxError as e:
                typer.echo(f"Error in service {async_so.operation_id}: {e}")
                typer.Exit()

    sync_tags = set([so.tag for so in service_ops])
    async_tags = set([so.tag for so in service_ops])

    for tag in sync_tags:
        services.append(Service(
            file_name=f"{tag}_service",
            operations=[so for so in service_ops if so.tag == tag and not so.async_client],
            content="\n".join([so.content for so in service_ops if so.tag == tag and not so.async_client]),
            async_client=False
        ))

    for tag in async_tags:
        services.append(Service(
            file_name=f"async_{tag}_service",
            operations=[so for so in service_ops if so.tag == tag and so.async_client],
            content="\n".join([so.content for so in service_ops if so.tag == tag and so.async_client]),
            async_client=True
        ))

    return services

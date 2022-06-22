from typing import Dict, List, Tuple

from openapi_schema_pydantic import PathItem, Operation

from src.openapi_python_generator.language_converters.python.jinja_config import JINJA_ENV, HTTPX_TEMPLATE
from src.openapi_python_generator.language_converters.python.model_generator import type_converter
from src.openapi_python_generator.models import Service, ServiceOperation

HTTP_OPERATIONS = ["get", "post", "put", "delete", "options", "head", "patch", "trace"]


def generate_params(operation: Operation) -> Tuple[List[str], List[str]]:
    if operation.parameters is None and operation.requestBody is None:
        return [], []

    params = []
    if operation.parameters is not None:
        for param in operation.parameters:
            params.append(f"{param.name} : {type_converter(param.param_schema, param.required)}")

    if operation.requestBody is not None:
        pass

    return params, []


def generate_operation_id(operation: Operation, http_op: str) -> str:
    return f"{http_op.lower()}_{operation.operationId.replace('-', '_')}"


def generate_query_params(operation: Operation) -> List[str]:
    if operation.parameters is None:
        return []

    params = []
    for param in operation.parameters:
        params.append(f"'{param.name}' : {param.name}")

    return params


def generate_return_type(operation: Operation) -> str:
    good_responses = [response for status_code, response in operation.responses.items() if status_code.startswith('2')]
    if len(good_responses) == 0:
        return "None"

    return "None"


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

            params, imports = generate_params(op)
            operation_id = generate_operation_id(op, http_operation)
            query_params = generate_query_params(op)
            return_type = generate_return_type(op)

            imports.append(return_type)

            sync_so = ServiceOperation(
                params=params,
                operation_id=operation_id,
                query_params=query_params,
                return_type=return_type,
                operation=op,
                pathItem=path,
                content="",
                async_client=False,
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
            )

            sync_so.content = JINJA_ENV.get_template(HTTPX_TEMPLATE).render(**sync_so.dict())
            async_so.content = JINJA_ENV.get_template(HTTPX_TEMPLATE).render(**async_so.dict())

            if op.tags is not None and len(op.tags) > 0:
                sync_so.tag = op.tags[0]
                async_so.tag = op.tags[0]

            service_ops.append(sync_so)
            service_ops.append(async_so)

    return services

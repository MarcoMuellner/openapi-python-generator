import re
from typing import Any, Dict, List, Literal, Optional, Tuple, Union

import click
from openapi_pydantic.v3 import (
    Operation,
    PathItem,
    Reference,
    Response,
    Schema,
)
from openapi_pydantic.v3.v3_0 import (
    Components as Components30,
)
from openapi_pydantic.v3.v3_0 import (
    MediaType as MediaType30,
)

# Import version-specific types for isinstance checks
from openapi_pydantic.v3.v3_0 import (
    Reference as Reference30,
)
from openapi_pydantic.v3.v3_0 import (
    Response as Response30,
)
from openapi_pydantic.v3.v3_0 import (
    Schema as Schema30,
)
from openapi_pydantic.v3.v3_0.parameter import Parameter as Parameter30
from openapi_pydantic.v3.v3_1 import (
    Components as Components31,
)
from openapi_pydantic.v3.v3_1 import (
    MediaType as MediaType31,
)
from openapi_pydantic.v3.v3_1 import (
    Reference as Reference31,
)
from openapi_pydantic.v3.v3_1 import (
    Response as Response31,
)
from openapi_pydantic.v3.v3_1 import (
    Schema as Schema31,
)
from openapi_pydantic.v3.v3_1.parameter import Parameter as Parameter31

from openapi_python_generator.language_converters.python import common
from openapi_python_generator.language_converters.python.common import normalize_symbol
from openapi_python_generator.language_converters.python.jinja_config import (
    create_jinja_env,
)
from openapi_python_generator.language_converters.python.model_generator import (
    type_converter,
)
from openapi_python_generator.models import (
    LibraryConfig,
    OpReturnType,
    Service,
    ServiceOperation,
    TypeConversion,
)

Components = Union[Components30, Components31]

_component_params: Optional[Dict[str, Union[Parameter30, Parameter31]]] = None


def _resolve_parameter_ref(
    param: Union[Parameter30, Parameter31, Reference30, Reference31],
) -> Optional[Union[Parameter30, Parameter31]]:
    if isinstance(param, (Parameter30, Parameter31)):
        return param

    if isinstance(param, (Reference, Reference30, Reference31)):
        if _component_params is None:
            return None
        ref_str = getattr(param, "ref", None)
        if ref_str and ref_str.startswith("#/components/parameters/"):
            param_name = ref_str.split("/")[-1]
            resolved = _component_params.get(param_name)
            if resolved is not None:
                return resolved

    return None


# Helper functions for isinstance checks across OpenAPI versions
def is_response_type(obj) -> bool:
    """Check if object is a Response from any OpenAPI version"""
    return isinstance(obj, (Response30, Response31))


def create_media_type_for_reference(
    reference_obj: Union[Response30, Reference30, Response31, Reference31],
):
    """Create a MediaType wrapper for a reference object, using the correct version"""
    # Check which version the reference object belongs to
    if isinstance(reference_obj, Reference30):
        return MediaType30(schema=reference_obj)  # type: ignore - pydantic issue with generics
    elif isinstance(reference_obj, Reference31):
        return MediaType31(schema=reference_obj)  # type: ignore - pydantic issue with generics
    else:
        # Fallback to v3.0 for generic Reference
        return MediaType30(schema=reference_obj)  # type: ignore - pydantic issue with generics


def is_media_type(obj) -> bool:
    """Check if object is a MediaType from any OpenAPI version"""
    return isinstance(obj, (MediaType30, MediaType31))


def is_reference_type(obj: Any) -> bool:
    """Check if object is a Reference type across different versions."""
    return isinstance(obj, (Reference, Reference30, Reference31))


def is_schema_type(obj: Any) -> bool:
    """Check if object is a Schema from any OpenAPI version"""
    return isinstance(obj, (Schema30, Schema31))


HTTP_OPERATIONS = ["get", "post", "put", "delete", "options", "head", "patch", "trace"]


def generate_body_param(operation: Operation) -> Union[str, None]:
    if operation.requestBody is None:
        return None
    else:
        if isinstance(operation.requestBody, Reference30) or isinstance(
            operation.requestBody, Reference31
        ):
            return "data.dict()"

        if operation.requestBody.content is None:
            return None  # pragma: no cover

        if operation.requestBody.content.get("application/json") is None:
            return None  # pragma: no cover

        media_type = operation.requestBody.content.get("application/json")

        if media_type is None:
            return None  # pragma: no cover

        if isinstance(
            media_type.media_type_schema, (Reference, Reference30, Reference31)
        ):
            return "data.dict()"
        elif hasattr(media_type.media_type_schema, "ref"):
            # Handle Reference objects from different OpenAPI versions
            return "data.dict()"
        elif isinstance(media_type.media_type_schema, (Schema, Schema30, Schema31)):
            schema = media_type.media_type_schema
            if schema.type == "array":
                return "[i.dict() for i in data]"
            elif schema.type == "object":
                return "data"
            else:
                raise Exception(
                    f"Unsupported schema type for request body: {schema.type}"
                )  # pragma: no cover
        else:
            raise Exception(
                f"Unsupported schema type for request body: {type(media_type.media_type_schema)}"
            )  # pragma: no cover


def generate_params(operation: Operation) -> str:
    def _generate_params_from_content(content: Any):
        # Accept reference from either 3.0 or 3.1
        if isinstance(content, (Reference, Reference30, Reference31)):
            return f"data : {content.ref.split('/')[-1]}"  # type: ignore
        elif isinstance(content, (Schema, Schema30, Schema31)):
            return f"data : {type_converter(content, True).converted_type}"  # type: ignore
        else:  # pragma: no cover
            raise Exception(f"Unsupported request body schema type: {type(content)}")

    if operation.parameters is None and operation.requestBody is None:
        return ""

    params = ""
    default_params = ""
    if operation.parameters is not None:
        for param in operation.parameters:
            resolved_param = _resolve_parameter_ref(param)
            if resolved_param is None:
                continue
            param = resolved_param
            converted_result = ""
            required = False
            param_name_cleaned = common.normalize_symbol(param.name)

            if isinstance(param.param_schema, Schema30) or isinstance(
                param.param_schema, Schema31
            ):
                converted_result = (
                    f"{param_name_cleaned} : {type_converter(param.param_schema, param.required).converted_type}"
                    + ("" if param.required else " = None")
                )
                required = param.required
            elif isinstance(param.param_schema, Reference30) or isinstance(
                param.param_schema, Reference31
            ):
                converted_result = (
                    f"{param_name_cleaned} : {param.param_schema.ref.split('/')[-1]}"
                    + (
                        ""
                        if isinstance(param, Reference30)
                        or isinstance(param, Reference31)
                        or param.required
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
        "application/octet-stream",
    ]

    if operation.requestBody is not None and not is_reference_type(
        operation.requestBody
    ):
        # Safe access only if it's a concrete RequestBody object
        rb_content = getattr(operation.requestBody, "content", None)
        if isinstance(rb_content, dict) and any(
            rb_content.get(i) is not None for i in operation_request_body_types
        ):
            get_keyword = [
                i for i in operation_request_body_types if rb_content.get(i)
            ][0]
            content = rb_content.get(get_keyword)
            if content is not None and hasattr(content, "media_type_schema"):
                mts = getattr(content, "media_type_schema", None)
                if isinstance(
                    mts,
                    (Reference, Reference30, Reference31, Schema, Schema30, Schema31),
                ):
                    params += f"{_generate_params_from_content(mts)}, "
                else:  # pragma: no cover
                    raise Exception(
                        f"Unsupported media type schema for {str(operation)}: {type(mts)}"
                    )
        # else: silently ignore unsupported body shapes (could extend later)
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
    operation: Operation, param_in: Literal["query", "header"] = "query"
):
    if operation.parameters is None:
        return []

    params = []
    for param in operation.parameters:
        resolved_param = _resolve_parameter_ref(param)
        if resolved_param is None or resolved_param.param_in != param_in:
            continue
        param_name_cleaned = common.normalize_symbol(resolved_param.name)
        params.append(f"{resolved_param.name!r} : {param_name_cleaned}")

    return params


def generate_query_params(operation: Operation) -> List[str]:
    return _generate_params(operation, "query")


def generate_header_params(operation: Operation) -> List[str]:
    return _generate_params(operation, "header")


def generate_return_type(operation: Operation) -> OpReturnType:
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
    media_type_schema = None

    if is_response_type(chosen_response):
        # It's a Response type, access content safely
        if hasattr(chosen_response, "content") and chosen_response.content is not None:  # type: ignore
            media_type_schema = chosen_response.content.get("application/json")  # type: ignore
    elif is_reference_type(chosen_response):
        media_type_schema = create_media_type_for_reference(chosen_response)

    if media_type_schema is None:
        return OpReturnType(
            type=None, status_code=good_responses[0][0], complex_type=False
        )

    if is_media_type(media_type_schema):
        inner_schema = getattr(media_type_schema, "media_type_schema", None)
        if is_reference_type(inner_schema):
            type_conv = TypeConversion(
                original_type=inner_schema.ref,  # type: ignore
                converted_type=inner_schema.ref.split("/")[-1],  # type: ignore
                import_types=[inner_schema.ref.split("/")[-1]],  # type: ignore
            )
            return OpReturnType(
                type=type_conv,
                status_code=good_responses[0][0],
                complex_type=True,
            )
        elif is_schema_type(inner_schema):
            converted_result = type_converter(inner_schema, True)  # type: ignore
            if "array" in converted_result.original_type and isinstance(
                converted_result.import_types, list
            ):
                matched = re.findall(r"List\[(.+)\]", converted_result.converted_type)
                if len(matched) > 0:
                    list_type = matched[0]
                else:  # pragma: no cover
                    raise Exception(
                        f"Unable to parse list type from {converted_result.converted_type}"
                    )
            else:
                list_type = None
            return OpReturnType(
                type=converted_result,
                status_code=good_responses[0][0],
                complex_type=bool(
                    converted_result.import_types
                    and len(converted_result.import_types) > 0
                ),
                list_type=list_type,
            )
        else:  # pragma: no cover
            raise Exception("Unknown media type schema type")
    elif media_type_schema is None:
        return OpReturnType(
            type=None,
            status_code=good_responses[0][0],
            complex_type=False,
        )
    else:
        raise Exception("Unknown media type schema type")  # pragma: no cover


def _generate_service_operation(
    op: Operation,
    path_name: str,
    async_type: bool,
    path: PathItem,
    http_operation: str,
    jinja_env: Any,
    library_config: LibraryConfig,
) -> ServiceOperation:
    try:
        path_level_params = []
        if hasattr(path, "parameters") and path.parameters is not None:
            path_level_params = [p for p in path.parameters if p is not None]
        if path_level_params:
            existing_names = set()
            if op.parameters is not None:
                for p in op.parameters:  # type: ignore
                    if isinstance(p, (Parameter30, Parameter31)):
                        existing_names.add(p.name)
            for p in path_level_params:
                if (
                    isinstance(p, (Parameter30, Parameter31))
                    and p.name not in existing_names
                ):
                    if op.parameters is None:
                        op.parameters = []  # type: ignore
                    op.parameters.append(p)  # type: ignore
    except Exception:  # pragma: no cover
        print(
            f"Error merging path-level parameters for {path_name}"
        )  # pragma: no cover
        pass

    params = generate_params(op)
    # Fallback: ensure all {placeholders} in path are present as function params
    try:
        placeholder_names = [
            m.group(1) for m in re.finditer(r"\{([^}/]+)\}", path_name)
        ]
        existing_param_names = {
            p.split(":")[0].strip() for p in params.split(",") if ":" in p
        }
        for ph in placeholder_names:
            norm_ph = common.normalize_symbol(ph)
            if norm_ph not in existing_param_names and norm_ph:
                params = f"{norm_ph}: Any, " + params
    except Exception:  # pragma: no cover
        print(
            f"Error ensuring path placeholders in params for {path_name}"
        )  # pragma: no cover
        pass
    operation_id = generate_operation_id(op, http_operation, path_name)
    query_params = generate_query_params(op)
    header_params = generate_header_params(op)
    return_type = generate_return_type(op)
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
        **so.model_dump()
    )

    if op.tags is not None and len(op.tags) > 0:
        so.tag = normalize_symbol(op.tags[0])

    try:
        compile(so.content, "<string>", "exec")
    except SyntaxError as e:  # pragma: no cover
        click.echo(f"Error in service {so.operation_id}: {e}")  # pragma: no cover

    return so


def generate_services(
    paths: Dict[str, PathItem],
    library_config: LibraryConfig,
    components: Optional[Components] = None,
) -> List[Service]:
    """
    Generates services from a paths object.
    :param paths: paths object to be converted
    :param library_config: Library configuration
    :param components: Optional OpenAPI components for resolving parameter references
    :return: List of services
    """
    global _component_params

    if (
        components is not None
        and hasattr(components, "parameters")
        and components.parameters is not None
    ):
        _component_params = {}
        for param_name, param_or_ref in components.parameters.items():
            if isinstance(param_or_ref, (Parameter30, Parameter31)):
                _component_params[param_name] = param_or_ref
    else:
        _component_params = None

    jinja_env = create_jinja_env()

    services = []
    service_ops = []
    for path_name, path in paths.items():
        clean_path_name = clean_up_path_name(path_name)
        for http_operation in HTTP_OPERATIONS:
            op = path.__getattribute__(http_operation)
            if op is None:
                continue

            if library_config.include_sync:
                sync_so = _generate_service_operation(
                    op,
                    clean_path_name,
                    False,
                    path,
                    http_operation,
                    jinja_env,
                    library_config,
                )
                service_ops.append(sync_so)

            if library_config.include_async:
                async_so = _generate_service_operation(
                    op,
                    clean_path_name,
                    True,
                    path,
                    http_operation,
                    jinja_env,
                    library_config,
                )
                service_ops.append(async_so)

    # Ensure every operation has a tag; fallback to "default" for untagged operations
    for so in service_ops:
        if not so.tag:
            so.tag = "default"

    tags = list({so.tag for so in service_ops})

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
                file_name=f"async_{tag}_service",
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


def clean_up_path_name(path_name: str) -> str:
    # Clean up path name: only replace dashes inside curly brackets for f-string compatibility, keep other dashes
    def _replace_bracket_dashes(match):
        return "{" + match.group(1).replace("-", "_") + "}"

    return re.sub(r"\{([^}/]+)\}", _replace_bracket_dashes, path_name)

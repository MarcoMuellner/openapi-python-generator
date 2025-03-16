import pytest
from openapi_pydantic.v3.v3_0 import (
    Operation, Reference, RequestBody, MediaType, Schema, Parameter,
    DataType, Response, ParameterLocation
)

from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.common import library_config_dict
from openapi_python_generator.language_converters.python.service_generator import (
    generate_body_param,
    generate_operation_id,
    generate_params,
    generate_query_params,
    generate_return_type,
    generate_services,
)
from openapi_python_generator.models import OpReturnType
from openapi_python_generator.models import TypeConversion

default_responses = {
    "200": Response(
        description="Default response",
        content={"application/json": MediaType(media_type_schema=Schema(type=DataType.OBJECT))}
    )
}

@pytest.mark.parametrize(
    "test_openapi_operation, expected_result",
    [
        (
            Operation(
                responses=default_responses,
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Reference(
                                ref="#/components/schemas/TestModel"
                            )
                        )
                    }
                )
            ),
            "data.dict()",
        ),
        (
            Operation(
                responses=default_responses,
                requestBody=Reference(ref="#/components/schemas/TestModel")
            ),
            "data.dict()",
        ),
        (
            Operation(
                responses=default_responses,
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Schema(
                                type=DataType.ARRAY,
                                items=Reference(ref="#/components/schemas/TestModel"),
                            )
                        )
                    }
                )
            ),
            "[i.dict() for i in data]",
        ),
        (Operation(responses=default_responses, requestBody=None), None),
    ],
)
def test_generate_body_param_pydanticv1(test_openapi_operation, expected_result, with_orjson_disabled, with_pydantic_v1):
    assert generate_body_param(test_openapi_operation) == expected_result


@pytest.mark.parametrize(
    "test_openapi_operation, expected_result",
    [
        (
            Operation(
                responses=default_responses,
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Reference(
                                ref="#/components/schemas/TestModel"
                            )
                        )
                    }
                )
            ),
            "data.model_dump(mode=\"json\")",
        ),
        (
            Operation(
                responses=default_responses,
                requestBody=Reference(ref="#/components/schemas/TestModel")
            ),
            "data.model_dump(mode=\"json\")",
        ),
        (
            Operation(
                responses=default_responses,
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Schema(
                                type=DataType.ARRAY,
                                items=Reference(ref="#/components/schemas/TestModel"),
                            )
                        )
                    }
                )
            ),
            "[i.model_dump(mode=\"json\") for i in data]",
        ),
        (Operation(responses=default_responses, requestBody=None), None),
    ],
)
def test_generate_body_param_pydanticv2(test_openapi_operation, expected_result, with_orjson_disabled, with_pydantic_v2):
    assert generate_body_param(test_openapi_operation) == expected_result


@pytest.mark.parametrize(
    "test_openapi_operation, expected_result",
    [
        (
            Operation(
                responses=default_responses,
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Reference(
                                ref="#/components/schemas/TestModel"
                            )
                        )
                    }
                )
            ),
            "data.model_dump()",
        ),
        (
            Operation(
                responses=default_responses,
                requestBody=Reference(ref="#/components/schemas/TestModel")
            ),
            "data.model_dump()",
        ),
        (
            Operation(
                responses=default_responses,
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Schema(
                                type=DataType.ARRAY,
                                items=Reference(ref="#/components/schemas/TestModel"),
                            )
                        )
                    }
                )
            ),
            "[i.model_dump() for i in data]",
        ),
        (Operation(responses=default_responses, requestBody=None), None),
    ],
)
def test_generate_body_param_orjson_pydanticv2(test_openapi_operation, expected_result, with_orjson_enabled, with_pydantic_v2):
    assert generate_body_param(test_openapi_operation) == expected_result

@pytest.mark.parametrize(
    "test_openapi_operation, expected_result",
    [
        (Operation(responses=default_responses, parameters=None, requestBody=None), ""),
        (
            Operation(
                responses=default_responses,
                parameters=[
                    Parameter(
                        name="test",
                        param_in=ParameterLocation.QUERY,
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    )
                ],
                requestBody=None,
            ),
            "test : TestModel, ",
        ),
        (
            Operation(
                responses=default_responses,
                parameters=[
                    Parameter(
                        name="test2",
                        param_in=ParameterLocation.PATH,
                        param_schema=Schema(type=DataType.STRING),
                        required=False,
                    )
                ],
            ),
            "test2 : Optional[str] = None, ",
        ),
        (
            Operation(
                responses=default_responses,
                parameters=[
                    Parameter(
                        name="test",
                        param_in=ParameterLocation.QUERY,
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in=ParameterLocation.PATH,
                        param_schema=Schema(type=DataType.STRING),
                        required=False,
                    ),
                ],
            ),
            "test : TestModel, test2 : Optional[str] = None, ",
        ),
        (
            Operation(
                responses=default_responses,
                parameters=[
                    Parameter(
                        name="test",
                        param_in=ParameterLocation.QUERY,
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in=ParameterLocation.PATH,
                        param_schema=Schema(type=DataType.STRING),
                        required=True,
                    ),
                ],
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Reference(
                                ref="#/components/schemas/TestModel"
                            )
                        )
                    }
                ),
            ),
            "test : TestModel, test2 : str, data : TestModel, ",
        ),
        (
            Operation(
                responses=default_responses,
                parameters=[
                    Parameter(
                        name="test",
                        param_in=ParameterLocation.QUERY,
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in=ParameterLocation.PATH,
                        param_schema=Schema(type=DataType.STRING),
                        required=True,
                    ),
                ],
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Schema(type=DataType.STRING)
                        )
                    }
                ),
            ),
            "test : TestModel, test2 : str, data : str, ",
        )
    ],
)
def test_generate_params(test_openapi_operation, expected_result):
    if isinstance(expected_result, Exception):
        with pytest.raises(Exception):
            generate_params(test_openapi_operation)
    else:
        assert generate_params(test_openapi_operation) == expected_result


@pytest.mark.parametrize(
    "test_openapi_operation, operation_type, expected_result",
    [
        (Operation(responses=default_responses, operationId="test"), "get", "test"),
        (Operation(responses=default_responses, operationId="test-test"), "get", "test_test"),
        (Operation(responses=default_responses, operationId="test"), "post", "test"),
        (Operation(responses=default_responses, operationId="test"), "GET", "test"),
        (Operation(responses=default_responses, operationId="test-test"), "GET", "test_test"),
        (Operation(responses=default_responses, operationId="test"), "POST", "test"),
    ],
)
def test_generate_operation_id(test_openapi_operation, operation_type, expected_result):
    assert generate_operation_id(test_openapi_operation, operation_type) == expected_result


@pytest.mark.parametrize(
    "test_openapi_operation, expected_result",
    [
        (Operation(responses=default_responses, parameters=None, requestBody=None), []),
        (
            Operation(
                responses=default_responses,
                parameters=[
                    Parameter(
                        name="test",
                        param_in=ParameterLocation.QUERY,
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    )
                ],
            ),
            ["'test' : test"],
        ),
        (
            Operation(
                responses=default_responses,
                parameters=[
                    Parameter(
                        name="test2",
                        param_in=ParameterLocation.PATH,
                        param_schema=Schema(type=DataType.STRING),
                        required=False,
                    )
                ],
            ),
            [],
        ),
        (
            Operation(
                responses=default_responses,
                parameters=[
                    Parameter(
                        name="test",
                        param_in=ParameterLocation.QUERY,
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in=ParameterLocation.QUERY,
                        param_schema=Schema(type=DataType.STRING),
                        required=True,
                    ),
                ]
            ),
            ["'test' : test", "'test2' : test2"],
        ),
    ],
)
def test_generate_query_params(test_openapi_operation, expected_result):
    assert generate_query_params(test_openapi_operation) == expected_result


@pytest.mark.parametrize(
    "test_openapi_operation, expected_result",
    [
        (
            Operation(responses={}),
            OpReturnType(type=None, status_code=200, complex_type=False),
        ),
        (
            Operation(responses={}),
            OpReturnType(type=None, status_code=200, complex_type=False),
        ),
        (
            Operation(
                responses={
                    "200": Response(
                        description="",
                        content={
                            "application/json": MediaType(
                                media_type_schema=Reference(
                                    ref="#/components/schemas/TestModel"
                                )
                            )
                        },
                    )
                }
            ),
            OpReturnType(
                type=TypeConversion(
                    original_type="#/components/schemas/TestModel",
                    converted_type="TestModel",
                    import_types=["TestModel"],
                ),
                status_code=200,
                complex_type=True,
            ),
        ),
        (
            Operation(
                responses={
                    "200": Response(
                        description="Successful Response",
                        content={
                            "application/json": MediaType(
                                media_type_schema=Schema(
                                    type=DataType.ARRAY,
                                    items=Reference(ref="#/components/schemas/User"),
                                )
                            )
                        },
                    )
                }
            ),
            OpReturnType(
                type=TypeConversion(
                    original_type="array<#/components/schemas/User>",
                    converted_type="List[User]",
                    import_types=["from .User import User"],
                ),
                status_code=200,
                complex_type=True,
                list_type="User",
            ),
        ),
        (
            Operation(
                responses={
                    "200": Response(
                        description="",
                        content={
                            "application/json": MediaType(
                                media_type_schema=Schema(type=DataType.STRING)
                            )
                        },
                    )
                }
            ),
            OpReturnType(
                type=TypeConversion(
                    original_type="string", converted_type="str", import_types=None
                ),
                status_code=200,
                complex_type=False,
            ),
        ),
    ],
)
def test_generate_return_type(test_openapi_operation, expected_result):
    assert generate_return_type(test_openapi_operation) == expected_result


def test_generate_services(model_data):
    result = generate_services(model_data.paths, library_config_dict[HTTPLibrary.httpx])
    for i in result:
        compile(i.content, "<string>", "exec")

    result = generate_services(model_data.paths, library_config_dict[HTTPLibrary.requests])
    for i in result:
        compile(i.content, "<string>", "exec")
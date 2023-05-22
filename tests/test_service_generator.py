import pytest
from openapi_schema_pydantic import MediaType
from openapi_schema_pydantic import Operation
from openapi_schema_pydantic import Parameter
from openapi_schema_pydantic import Reference
from openapi_schema_pydantic import RequestBody
from openapi_schema_pydantic import Response
from openapi_schema_pydantic import Schema

from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.common import library_config_dict
from openapi_python_generator.language_converters.python.service_generator import (
    generate_body_param,
)
from openapi_python_generator.language_converters.python.service_generator import (
    generate_operation_id,
)
from openapi_python_generator.language_converters.python.service_generator import (
    generate_params,
)
from openapi_python_generator.language_converters.python.service_generator import (
    generate_query_params,
)
from openapi_python_generator.language_converters.python.service_generator import (
    generate_return_type,
)
from openapi_python_generator.language_converters.python.service_generator import (
    generate_services,
)
from openapi_python_generator.models import OpReturnType
from openapi_python_generator.models import TypeConversion


@pytest.mark.parametrize(
    "test_openapi_operation, expected_result",
    [
        (
            Operation(
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
            Operation(requestBody=Reference(ref="#/components/schemas/TestModel")),
            "data.dict()",
        ),
        (
            Operation(
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Schema(
                                type="array",
                                items=Reference(ref="#/components/schemas/TestModel"),
                            )
                        )
                    }
                )
            ),
            "[i.dict() for i in data]",
        ),
        (Operation(requestBody=None), None),
    ],
)
def test_generate_body_param(test_openapi_operation, expected_result):
    assert generate_body_param(test_openapi_operation) == expected_result


@pytest.mark.parametrize(
    "test_openapi_operation, expected_result",
    [
        (Operation(parameters=None, requestBody=None), ""),
        (
            Operation(
                parameters=[
                    Parameter(
                        name="test",
                        param_in="query",
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
                parameters=[
                    Parameter(
                        name="test2",
                        param_in="path",
                        param_schema=Schema(type="string"),
                        required=False,
                    )
                ],
            ),
            "test2 : Optional[str] = None, ",
        ),
        (
            Operation(
                parameters=[
                    Parameter(
                        name="test",
                        param_in="query",
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in="path",
                        param_schema=Schema(type="string"),
                        required=False,
                    ),
                ],
            ),
            "test : TestModel, test2 : Optional[str] = None, ",
        ),
        (
            Operation(
                parameters=[
                    Parameter(
                        name="test",
                        param_in="query",
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in="path",
                        param_schema=Schema(type="string"),
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
                parameters=[
                    Parameter(
                        name="test",
                        param_in="query",
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in="path",
                        param_schema=Schema(type="string"),
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
                parameters=[
                    Parameter(
                        name="test",
                        param_in="query",
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in="path",
                        param_schema=Schema(type="string"),
                        required=True,
                    ),
                ],
                requestBody=RequestBody(
                    content={
                        "application/json": MediaType(
                            media_type_schema=Schema(type="string")
                        )
                    }
                ),
            ),
            "test : TestModel, test2 : str, data : str, ",
        ),
        (
            Operation(
                parameters=[
                    Parameter(
                        name="test",
                        param_in="query",
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in="path",
                        param_schema=Schema(type="string"),
                        required=True,
                    ),
                ],
                requestBody=RequestBody(
                    content=MediaType(
                        example="",
                        examples=[],
                        encoding={},
                        media_type_schema=Schema(type="string"),
                    )
                ),
            ),
            Exception(),
        ),
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
        (Operation(operationId="test"), "get", "test"),
        (Operation(operationId="test-test"), "get", "test_test"),
        (Operation(operationId="test"), "post", "test"),
        (Operation(operationId="test"), "GET", "test"),
        (Operation(operationId="test-test"), "GET", "test_test"),
        (Operation(operationId="test"), "POST", "test"),
    ],
)
def test_generate_operation_id(test_openapi_operation, operation_type, expected_result):
    assert (
        generate_operation_id(test_openapi_operation, operation_type) == expected_result
    )


@pytest.mark.parametrize(
    "test_openapi_operation, expected_result",
    [
        (Operation(parameters=None, requestBody=None), []),
        (
            Operation(
                parameters=[
                    Parameter(
                        name="test",
                        param_in="query",
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    )
                ],
            ),
            ["'test' : test"],
        ),
        (
            Operation(
                parameters=[
                    Parameter(
                        name="test2",
                        param_in="path",
                        param_schema=Schema(type="string"),
                        required=False,
                    )
                ],
            ),
            [],
        ),
        (
            Operation(
                parameters=[
                    Parameter(
                        name="test",
                        param_in="query",
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in="path",
                        param_schema=Schema(type="string"),
                        required=False,
                    ),
                ],
            ),
            ["'test' : test"],
        ),
        (
            Operation(
                parameters=[
                    Parameter(
                        name="test",
                        param_in="query",
                        param_schema=Reference(ref="#/components/schemas/TestModel"),
                        required=True,
                    ),
                    Parameter(
                        name="test2",
                        param_in="query",
                        param_schema=Schema(type="string"),
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
            Operation(responses=None),
            OpReturnType(type=None, status_code="200", complex_type="False"),
        ),
        (
            Operation(responses=[]),
            OpReturnType(type=None, status_code="200", complex_type="False"),
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
                status_code="200",
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
                                media_type_schema=Reference(
                                    ref="#/components/schemas/User"
                                )
                            )
                        },
                    )
                }
            ),
            OpReturnType(
                type=TypeConversion(
                    original_type="#/components/schemas/User",
                    converted_type="User",
                    import_types=["User"],
                ),
                status_code="200",
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
                                    type="array",
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
                status_code="200",
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
                                media_type_schema=Schema(type="string")
                            )
                        },
                    )
                }
            ),
            OpReturnType(
                type=TypeConversion(
                    original_type="string", converted_type="str", import_types=None
                ),
                status_code="200",
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

    result = generate_services(
        model_data.paths, library_config_dict[HTTPLibrary.requests]
    )

    for i in result:
        compile(i.content, "<string>", "exec")

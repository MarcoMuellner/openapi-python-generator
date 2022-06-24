import pytest
from openapi_schema_pydantic import Operation, Parameter, RequestBody, MediaType, Reference, Schema, Response

from openapi_python_generator.language_converters.python.service_generator import generate_body_param, \
    generate_params, generate_operation_id, generate_query_params, generate_return_type, generate_services
from openapi_python_generator.models import OpReturnType


@pytest.mark.parametrize("test_openapi_operation, expected_result", [
    (Operation(requestBody=RequestBody(content={
        "application/json": MediaType(
            media_type_schema=Reference(ref="#/components/schemas/TestModel")
        )
    })), "data"),
    (Operation(requestBody=None), None)
])
def test_generate_body_param(test_openapi_operation, expected_result):
    assert generate_body_param(test_openapi_operation) == expected_result


@pytest.mark.parametrize("test_openapi_operation, expected_result", [
    (Operation(parameters=None, requestBody=None), []),
    (Operation(parameters=[
        Parameter(name="test", param_in="query", param_schema=Reference(ref="#/components/schemas/TestModel"),
                  required=True)
    ],
        requestBody=None), ["test : TestModel"]),
    (Operation(
        parameters=[Parameter(name="test2", param_in="path", param_schema=Schema(type="string"), required=False)], ),
     ["test2 : Optional[str] = None"]),
    (Operation(parameters=[
        Parameter(name="test", param_in="query", param_schema=Reference(ref="#/components/schemas/TestModel"),
                  required=True),
        Parameter(name="test2", param_in="path", param_schema=Schema(type="string"), required=False)
    ], ), ["test : TestModel", "test2 : Optional[str] = None"]),
    (Operation(parameters=[
        Parameter(name="test", param_in="query", param_schema=Reference(ref="#/components/schemas/TestModel"),
                  required=True),
        Parameter(name="test2", param_in="path", param_schema=Schema(type="string"), required=True),
    ], requestBody=RequestBody(content={
        "application/json": MediaType(
            media_type_schema=Reference(ref="#/components/schemas/TestModel")
        )
    })), ["test : TestModel", "test2 : str", "data : TestModel"]),
    (Operation(parameters=[
        Parameter(name="test", param_in="query", param_schema=Reference(ref="#/components/schemas/TestModel"),
                  required=True),
        Parameter(name="test2", param_in="path", param_schema=Schema(type="string"), required=True),
    ], requestBody=RequestBody(content={
        "application/json": MediaType(
            media_type_schema=Reference(ref="#/components/schemas/TestModel")
        )
    })), ["test : TestModel", "test2 : str", "data : TestModel"])

])
def test_generate_params(test_openapi_operation, expected_result):
    assert generate_params(test_openapi_operation) == expected_result


@pytest.mark.parametrize("test_openapi_operation, operation_type, expected_result", [
    (Operation(operationId="test"), "get", "get_test"),
    (Operation(operationId="test-test"), "get", "get_test_test"),
    (Operation(operationId="test"), "post", "post_test"),
    (Operation(operationId="test"), "GET", "get_test"),
    (Operation(operationId="test-test"), "GET", "get_test_test"),
    (Operation(operationId="test"), "POST", "post_test")
])
def test_generate_operation_id(test_openapi_operation, operation_type, expected_result):
    assert generate_operation_id(test_openapi_operation, operation_type) == expected_result


@pytest.mark.parametrize("test_openapi_operation, expected_result", [
    (Operation(parameters=None, requestBody=None), []),
    (Operation(parameters=[
        Parameter(name="test", param_in="query", param_schema=Reference(ref="#/components/schemas/TestModel"),
                  required=True)
    ], ), ["'test' : test"]),
    (Operation(
        parameters=[Parameter(name="test2", param_in="path", param_schema=Schema(type="string"), required=False)], ),
     []),
    (Operation(parameters=[
        Parameter(name="test", param_in="query", param_schema=Reference(ref="#/components/schemas/TestModel"),
                  required=True),
        Parameter(name="test2", param_in="path", param_schema=Schema(type="string"), required=False)
    ], ), ["'test' : test"]),
    (Operation(parameters=[
        Parameter(name="test", param_in="query", param_schema=Reference(ref="#/components/schemas/TestModel"),
                  required=True),
        Parameter(name="test2", param_in="query", param_schema=Schema(type="string"), required=True),
    ]), ["'test' : test", "'test2' : test2"])
])
def test_generate_query_params(test_openapi_operation, expected_result):
    assert generate_query_params(test_openapi_operation) == expected_result


@pytest.mark.parametrize("test_openapi_operation, expected_result", [
    (Operation(responses=None), OpReturnType(type="None", status_code="200", complex_type="False")),
    (Operation(responses=[]), OpReturnType(type="None", status_code="200", complex_type="False")),
    (Operation(responses={"200": Response(description="", content={
        "application/json": MediaType(media_type_schema=Reference(ref="#/components/schemas/TestModel"))})}),
     OpReturnType(type="TestModel", status_code='200', complex_type=True)),
    (Operation(responses={"200": Response(description="", content={
        "application/json": MediaType(media_type_schema=Schema(type="string"))})}),
     OpReturnType(type="str", status_code='200', complex_type=False))
])
def test_generate_return_type(test_openapi_operation, expected_result):
    assert generate_return_type(test_openapi_operation) == expected_result


def test_generate_services(model_data):
    result = generate_services(model_data.paths)

    for i in result:
        compile(i.content, '<string>', 'exec')
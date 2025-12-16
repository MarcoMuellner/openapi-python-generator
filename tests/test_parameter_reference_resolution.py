from openapi_pydantic.v3.v3_0 import (
    Components as Components30,
    Reference as Reference30,
    PathItem as PathItem30,
    Operation as Operation30,
    Response as Response30,
    MediaType as MediaType30,
    Schema as Schema30,
)
from openapi_pydantic.v3.v3_0.parameter import Parameter as Parameter30
from openapi_pydantic.v3.v3_1 import (
    Components as Components31,
    Reference as Reference31,
    PathItem as PathItem31,
    Operation as Operation31,
    Response as Response31,
    MediaType as MediaType31,
    Schema as Schema31,
)
from openapi_pydantic.v3.v3_1.parameter import Parameter as Parameter31

from openapi_python_generator.common import HTTPLibrary, library_config_dict
from openapi_python_generator.language_converters.python.service_generator import (
    generate_services,
    _resolve_parameter_ref,
)
import openapi_python_generator.language_converters.python.service_generator as sg


def test_resolve_parameter_ref_returns_direct_parameter():
    param = Parameter30(
        name="lang",
        param_in="query",
        required=True,
        param_schema=Schema30(type="string"),
    )
    assert _resolve_parameter_ref(param) is param


def test_resolve_parameter_ref_resolves_reference():
    lang_param = Parameter30(
        name="lang",
        param_in="query",
        required=True,
        param_schema=Schema30(type="string"),
    )
    sg._component_params = {"LangParameter": lang_param}

    try:
        ref = Reference30(ref="#/components/parameters/LangParameter")
        assert _resolve_parameter_ref(ref) is lang_param
    finally:
        sg._component_params = None


def test_resolve_parameter_ref_returns_none_for_missing():
    sg._component_params = {}
    try:
        ref = Reference30(ref="#/components/parameters/NonExistent")
        assert _resolve_parameter_ref(ref) is None
    finally:
        sg._component_params = None


def test_generate_services_resolves_parameter_references_30():
    components = Components30(
        parameters={
            "LangParameter": Parameter30(
                name="lang",
                param_in="query",
                required=True,
                param_schema=Schema30(type="string"),
            )
        }
    )
    paths = {
        "/test": PathItem30(
            get=Operation30(
                operationId="getTest",
                parameters=[Reference30(ref="#/components/parameters/LangParameter")],
                responses={
                    "200": Response30(
                        description="Success",
                        content={
                            "application/json": MediaType30(
                                media_type_schema=Schema30(type="object")
                            )
                        },
                    )
                },
            )
        )
    }

    services = generate_services(
        paths, library_config_dict[HTTPLibrary.httpx], components
    )

    sync_services = [s for s in services if not s.async_client]
    assert len(sync_services) > 0
    assert "lang" in sync_services[0].operations[0].params


def test_generate_services_resolves_parameter_references_31():
    components = Components31(
        parameters={
            "TypeParameter": Parameter31(
                name="type",
                param_in="query",
                required=False,
                param_schema=Schema31(type="string"),
            )
        }
    )
    paths = {
        "/items": PathItem31(
            get=Operation31(
                operationId="listItems",
                parameters=[Reference31(ref="#/components/parameters/TypeParameter")],
                responses={
                    "200": Response31(
                        description="Success",
                        content={
                            "application/json": MediaType31(
                                media_type_schema=Schema31(type="array")
                            )
                        },
                    )
                },
            )
        )
    }

    services = generate_services(
        paths, library_config_dict[HTTPLibrary.httpx], components
    )

    sync_services = [s for s in services if not s.async_client]
    assert len(sync_services) > 0
    assert "type" in sync_services[0].operations[0].params


def test_generate_services_handles_mixed_parameters():
    components = Components30(
        parameters={
            "LangParameter": Parameter30(
                name="lang",
                param_in="query",
                required=True,
                param_schema=Schema30(type="string"),
            )
        }
    )
    paths = {
        "/test/{id}": PathItem30(
            get=Operation30(
                operationId="getTestById",
                parameters=[
                    Parameter30(
                        name="id",
                        param_in="path",
                        required=True,
                        param_schema=Schema30(type="integer"),
                    ),
                    Reference30(ref="#/components/parameters/LangParameter"),
                ],
                responses={
                    "200": Response30(
                        description="Success",
                        content={
                            "application/json": MediaType30(
                                media_type_schema=Schema30(type="object")
                            )
                        },
                    )
                },
            )
        )
    }

    services = generate_services(
        paths, library_config_dict[HTTPLibrary.httpx], components
    )

    sync_services = [s for s in services if not s.async_client]
    params = sync_services[0].operations[0].params
    assert "id" in params
    assert "lang" in params

import asyncio
from datetime import datetime, UTC

import httpx
import pytest
import responses
from aiohttp import web
from urllib.parse import urlparse

from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.generate_data import generate_data

from .conftest import test_data_path
from .conftest import test_result_path


def test_get_auth_token_without_env(model_data_with_cleanup):
    generate_data(test_data_path, test_result_path)

    _locals = locals()

    exec(
        "from .test_result import *\nassert APIConfig().get_access_token() is None",
        globals(),
        _locals,
    )


def test_set_auth_token():
    generate_data(test_data_path, test_result_path)

    _locals = locals()
    program = """from .test_result import APIConfig
api_config = APIConfig()
assert api_config.get_access_token() is None
api_config.set_access_token('foo_bar')
assert api_config.get_access_token() == 'foo_bar'
    """
    exec(
        program,
        globals(),
        _locals,
    )


@pytest.mark.respx(assert_all_called=False, assert_all_mocked=False)
@pytest.mark.parametrize(
    "library, use_orjson, custom_ip, openapi_version",
    [
        # OpenAPI 3.0 tests
        (HTTPLibrary.httpx, False, None, "3.0"),
        (HTTPLibrary.requests, False, None, "3.0"),
        (HTTPLibrary.httpx, True, None, "3.0"),
        (HTTPLibrary.requests, True, None, "3.0"),
        (HTTPLibrary.httpx, False, "http://localhost:5000", "3.0"),
        (HTTPLibrary.requests, False, "http://localhost:5000", "3.0"),
        (HTTPLibrary.httpx, True, "http://localhost:5000", "3.0"),
        (HTTPLibrary.requests, True, "http://localhost:5000", "3.0"),
        # OpenAPI 3.1 tests (same spec for now if 3.1 test file not present)
        (HTTPLibrary.httpx, False, None, "3.1"),
        (HTTPLibrary.requests, False, None, "3.1"),
        (HTTPLibrary.httpx, True, None, "3.1"),
        (HTTPLibrary.requests, True, None, "3.1"),
        (HTTPLibrary.httpx, False, "http://localhost:5000", "3.1"),
        (HTTPLibrary.requests, False, "http://localhost:5000", "3.1"),
        (HTTPLibrary.httpx, True, "http://localhost:5000", "3.1"),
        (HTTPLibrary.requests, True, "http://localhost:5000", "3.1"),
        # aiohttp (async) tests
        (HTTPLibrary.aiohttp, True, None, "3.0"),
        (HTTPLibrary.aiohttp, False, None, "3.0"),
        (HTTPLibrary.aiohttp, True, "http://127.0.0.1:5001", "3.0"),
        (HTTPLibrary.aiohttp, False, "http://127.0.0.1:5002", "3.0"),
        (HTTPLibrary.aiohttp, True, None, "3.1"),
        (HTTPLibrary.aiohttp, False, None, "3.1"),
        (HTTPLibrary.aiohttp, True, "http://127.0.0.1:5003", "3.1"),
        (HTTPLibrary.aiohttp, False, "http://127.0.0.1:5004", "3.1"),
    ],
)
def test_generate_code(
    model_data_with_cleanup, library, use_orjson, custom_ip, openapi_version, respx_mock
):
    # Create unique temp directory for this test combination
    import tempfile
    import shutil
    import sys
    import importlib
    from pathlib import Path

    # Select appropriate test data file based on OpenAPI version
    test_data_folder = Path(__file__).parent / "test_data"
    spec_31 = test_data_folder / "test_api_31.json"
    if openapi_version == "3.1" and spec_31.exists():
        spec_file = spec_31
    else:
        spec_file = test_data_folder / "test_api.json"

    # Create unique test directory based on parameters
    test_name = (
        f"test_result_{library.value}_{use_orjson}_{custom_ip or 'none'}_{openapi_version}"
        .replace(":", "_")
        .replace("/", "_")
        .replace(".", "_")
    )
    temp_dir = Path(tempfile.gettempdir()) / test_name

    # Clean up any existing directory
    if temp_dir.exists():
        shutil.rmtree(temp_dir)

    # Generate data to unique directory
    generate_data(spec_file, temp_dir, library, use_orjson=use_orjson)

    # Add temp directory to sys.path for imports
    sys.path.insert(0, str(temp_dir.parent))

    # Import generated modules
    api_config_module = importlib.import_module(f"{temp_dir.name}.api_config")
    if library == HTTPLibrary.aiohttp:
        general_service_module = importlib.import_module(
            f"{temp_dir.name}.services.async_general_service"
        )
    else:
        general_service_module = importlib.import_module(
            f"{temp_dir.name}.services.general_service"
        )
    models_module = importlib.import_module(f"{temp_dir.name}.models")

    # Create API config instance
    api_config_instance = api_config_module.APIConfig()

    # Get the base URL from the API config
    if custom_ip is not None:
        api_config_instance.base_path = custom_ip
        base_url = custom_ip
    else:
        base_url = api_config_instance.base_path

    # Ensure base_url doesn't have trailing slash for consistent URL construction
    base_url = base_url.rstrip("/")

    # Set up mocking based on HTTP library
    if library == HTTPLibrary.httpx:
        # Use respx for httpx
        root_route, get_users_route, get_teams_route = _setup_httpx_mocks(
            respx_mock, base_url
        )
    elif library == HTTPLibrary.requests:
        # Use responses for requests library
        with responses.RequestsMock() as responses_mock:
            routes = _setup_requests_mocks(responses_mock, base_url)
            root_route, get_users_route, get_teams_route = routes
            _run_service_tests(
                general_service_module,
                models_module,
                api_config_instance,
                custom_ip,
                root_route,
                get_users_route,
                get_teams_route,
                library,
            )
        return  # Early return for requests to avoid running tests outside context
    elif library == HTTPLibrary.aiohttp:
        # Run async aiohttp server and client tests
        asyncio.run(
            _run_service_tests_aiohttp(
                general_service_module, models_module, api_config_instance, custom_ip
            )
        )
        return

    # Run tests for httpx (respx context is already active)
    _run_service_tests(
        general_service_module,
        models_module,
        api_config_instance,
        custom_ip,
        root_route,
        get_users_route,
        get_teams_route,
        library,
    )


def _setup_httpx_mocks(respx_mock, base_url):
    """Set up HTTP mocks for httpx using respx"""
    root_url = f"{base_url}/"

    root_route = respx_mock.get(root_url).mock(
        return_value=httpx.Response(200, json={"message": "Hello World"})
    )

    get_users_route = respx_mock.get(f"{base_url}/users").mock(
        return_value=httpx.Response(
            200,
            json=[
                dict(
                    id=1,
                    username="user1",
                    email="x@y.com",
                    password="123456",
                    is_active=True,
                    created_at=datetime.now(UTC).isoformat(),
                ),
                dict(
                    id=2,
                    username="user2",
                    email="x@y.com",
                    password="123456",
                    is_active=True,
                    created_at=datetime.now(UTC).isoformat(),
                ),
            ],
        )
    )

    get_teams_route = respx_mock.get(f"{base_url}/teams").mock(
        return_value=httpx.Response(
            200,
            json=[
                dict(
                    id=1,
                    name="team1",
                    description="team1",
                    is_active=True,
                    created_at=datetime.now(UTC).isoformat(),
                    updated_at=datetime.now(UTC).isoformat(),
                ),
                dict(
                    id=2,
                    name="team2",
                    description="team2",
                    is_active=True,
                    created_at=datetime.now(UTC).isoformat(),
                    updated_at=datetime.now(UTC).isoformat(),
                ),
            ],
        )
    )

    return root_route, get_users_route, get_teams_route


def _setup_requests_mocks(responses_mock, base_url):
    root_url = f"{base_url}/"

    root_route = responses_mock.add(
        responses.GET, root_url, json={"message": "Hello World"}, status=200
    )

    get_users_route = responses_mock.add(
        responses.GET,
        f"{base_url}/users",
        json=[
            dict(
                id="1",  # String ID for compatibility
                username="user1",
                email="x@y.com",
                password="123456",
                is_active=True,
                created_at=datetime.now(UTC).isoformat(),
            ),
            dict(
                id="2",  # String ID for compatibility
                username="user2",
                email="x@y.com",
                password="123456",
                is_active=True,
                created_at=datetime.now(UTC).isoformat(),
            ),
        ],
        status=200,
    )

    get_teams_route = responses_mock.add(
        responses.GET,
        f"{base_url}/teams",
        json=[
            dict(
                id="1",  # String ID for compatibility
                name="team1",
                description="team1",
                is_active=True,
                created_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat(),
            ),
            dict(
                id="2",  # String ID for compatibility
                name="team2",
                description="team2",
                is_active=True,
                created_at=datetime.now(UTC).isoformat(),
                updated_at=datetime.now(UTC).isoformat(),
            ),
        ],
        status=200,
    )

    return root_route, get_users_route, get_teams_route


def _run_service_tests(
    general_service_module,
    models_module,
    api_config_instance,
    custom_ip,
    root_route,
    get_users_route,
    get_teams_route,
    library,
):
    """Run the actual service tests"""
    passed_api_config = None

    if custom_ip:
        passed_api_config = api_config_instance

    # Test root endpoint
    resp_result = general_service_module.root__get(passed_api_config)
    assert isinstance(resp_result, models_module.RootResponse)

    # Check if route was called (different APIs for respx vs responses)
    if library == HTTPLibrary.httpx:
        assert root_route.called
    else:
        assert root_route.call_count > 0

    # Test get users
    resp_result = general_service_module.get_users_users_get(passed_api_config)
    assert isinstance(resp_result, list)
    assert isinstance(resp_result[0], models_module.User)
    assert isinstance(resp_result[1], models_module.User)

    if library == HTTPLibrary.httpx:
        assert get_users_route.called
    else:
        assert get_users_route.call_count > 0

    # Test get teams
    resp_result = general_service_module.get_teams_teams_get(passed_api_config)
    assert isinstance(resp_result, list)

    if library == HTTPLibrary.httpx:
        assert get_teams_route.called
    else:
        assert get_teams_route.call_count > 0

    print("Service generator E2E passed")


async def _run_service_tests_aiohttp(
    general_service_module, models_module, api_config_instance, custom_ip
):
    """Run service tests against a live aiohttp test server."""
    async def handle_root(request):
        return web.json_response({"message": "Hello World"})

    async def handle_users(request):
        return web.json_response(
            [
                dict(
                    id=1,
                    username="user1",
                    email="x@y.com",
                    password="123456",
                    is_active=True,
                    created_at=datetime.now(UTC).isoformat(),
                ),
                dict(
                    id=2,
                    username="user2",
                    email="x@y.com",
                    password="123456",
                    is_active=True,
                    created_at=datetime.now(UTC).isoformat(),
                ),
            ]
        )

    async def handle_teams(request):
        return web.json_response(
            [
                dict(
                    id=1,
                    name="team1",
                    description="team1",
                    is_active=True,
                    created_at=datetime.now(UTC).isoformat(),
                    updated_at=datetime.now(UTC).isoformat(),
                ),
                dict(
                    id=2,
                    name="team2",
                    description="team2",
                    is_active=True,
                    created_at=datetime.now(UTC).isoformat(),
                    updated_at=datetime.now(UTC).isoformat(),
                ),
            ]
        )

    app = web.Application()
    app.router.add_get("/", handle_root)
    app.router.add_get("/users", handle_users)
    app.router.add_get("/teams", handle_teams)

    runner = web.AppRunner(app)
    await runner.setup()

    host = "127.0.0.1"
    port = 0
    scheme = "http"
    if custom_ip:
        parsed = urlparse(custom_ip)
        if parsed.hostname:
            host = parsed.hostname
        if parsed.port:
            port = parsed.port
        if parsed.scheme:
            scheme = parsed.scheme

    site = web.TCPSite(runner, host, port)
    await site.start()

    if port == 0:
        # Retrieve the assigned ephemeral port
        sockets = site._server.sockets  # type: ignore[attr-defined]
        assert sockets and len(sockets) > 0
        port = sockets[0].getsockname()[1]

    base_url = f"{scheme}://{host}:{port}"
    api_config_instance.base_path = base_url

    try:
        # Call async generated functions
        resp_result = await general_service_module.root__get(api_config_instance)
        assert isinstance(resp_result, models_module.RootResponse)

        resp_users = await general_service_module.get_users_users_get(
            api_config_instance
        )
        assert isinstance(resp_users, list)
        assert isinstance(resp_users[0], models_module.User)

        resp_teams = await general_service_module.get_teams_teams_get(
            api_config_instance
        )
        assert isinstance(resp_teams, list)
    finally:
        await runner.cleanup()

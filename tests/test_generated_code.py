import json
import os
import traceback
from datetime import datetime

import orjson
import pytest
import respx
from httpx import Response

from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.common import library_config_dict
from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.language_converters.python.generator import generator

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


@pytest.mark.parametrize(
    "library, use_orjson, custom_ip",
    [
        (HTTPLibrary.httpx, False, None),
        (HTTPLibrary.requests, False, None),
        (HTTPLibrary.httpx, True, None),
        (HTTPLibrary.requests, True, None),
        (HTTPLibrary.aiohttp, True, None),
        (HTTPLibrary.aiohttp, False, None),
        (HTTPLibrary.httpx, False, "http://localhost:5000"),
        (HTTPLibrary.requests, False, "http://localhost:5000"),
        (HTTPLibrary.httpx, True, "http://localhost:5000"),
        (HTTPLibrary.requests, True, "http://localhost:5000"),
        (HTTPLibrary.aiohttp, True, "http://localhost:5000"),
        (HTTPLibrary.aiohttp, False, "http://localhost:5000"),
    ],
)
@respx.mock
def test_generate_code(model_data_with_cleanup, library, use_orjson, custom_ip, with_pydantic_v2):
    generate_data(test_data_path, test_result_path, library, use_orjson=use_orjson)
    result = generator(model_data_with_cleanup, library_config_dict[library])

    if custom_ip is not None:
        api_config_custom = result.api_config
        api_config_custom.base_url = custom_ip
    else:
        api_config_custom = result.api_config

    # Testing root access
    root_route = respx.get(f"{api_config_custom.base_url}/").mock(
        return_value=Response(
            status_code=200, content=json.dumps({"message": "Hello World"})
        )
    )
    get_users_route = respx.get(f"{api_config_custom.base_url}/users").mock(
        return_value=Response(
            status_code=200,
            content=json.dumps(
                [
                    dict(
                        id=1,
                        username="user1",
                        email="x@y.com",
                        password="123456",
                        is_active=True,
                        created_at=datetime.utcnow().isoformat(),
                    ),
                    dict(
                        id=2,
                        username="user2",
                        email="x@y.com",
                        password="123456",
                        is_active=True,
                        created_at=datetime.utcnow().isoformat(),
                    ),
                ]
            ),
        )
    )
    get_user_route = respx.get(f"{api_config_custom.base_url}/users/{1}").mock(
        return_value=Response(
            status_code=200,
            content=json.dumps(
                dict(
                    id=2,
                    username="user2",
                    email="x@y.com",
                    password="123456",
                    is_active=True,
                    created_at=datetime.utcnow().isoformat(),
                )
            ),
        )
    )
    post_user_route = respx.post(f"{api_config_custom.base_url}/users").mock(
        return_value=Response(
            status_code=201,
            content=json.dumps(
                dict(
                    id=2,
                    username="user2",
                    email="x@y.com",
                    password="123456",
                    is_active=True,
                    created_at=datetime.utcnow().isoformat(),
                )
            ),
        )
    )
    update_user_route = respx.patch(f"{api_config_custom.base_url}/users/{1}").mock(
        return_value=Response(
            status_code=200,
            content=json.dumps(
                dict(
                    id=2,
                    username="user2",
                    email="x@y.com",
                    password="123456",
                    is_active=True,
                )
            ),
        )
    )
    delete_user_route = respx.delete(f"{api_config_custom.base_url}/users/{1}").mock(
        return_value=Response(status_code=204, content=json.dumps(None))
    )

    get_teams_route = respx.get(f"{api_config_custom.base_url}/teams").mock(
        return_value=Response(
            status_code=200,
            content=orjson.dumps(
                [
                    dict(
                        id=1,
                        name="team1",
                        description="team1",
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    ),
                    dict(
                        id=2,
                        name="team2",
                        description="team2",
                        is_active=True,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow(),
                    ),
                ]
            ),
        )
    )

    get_team_route = respx.get(f"{api_config_custom.base_url}/teams/{1}").mock(
        return_value=Response(
            status_code=200,
            content=orjson.dumps(
                dict(
                    id=1,
                    name="team1",
                    description="team1",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            ),
        )
    )
    post_team_route = respx.post(f"{api_config_custom.base_url}/teams").mock(
        return_value=Response(
            status_code=201,
            content=orjson.dumps(
                dict(
                    id=1,
                    name="team1",
                    description="team1",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            ),
        )
    )

    update_team_route = respx.patch(f"{api_config_custom.base_url}/teams/{1}").mock(
        return_value=Response(
            status_code=200,
            content=orjson.dumps(
                dict(
                    id=1,
                    name="team1",
                    description="team1",
                    is_active=True,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                )
            ),
        )
    )

    delete_team_route = respx.delete(f"{api_config_custom.base_url}/teams/{1}").mock(
        return_value=Response(status_code=204, content=json.dumps(None))
    )

    passed_api_config = None

    if custom_ip:
        from .test_result.api_config import APIConfig

        passed_api_config = APIConfig()
        passed_api_config.base_path = custom_ip

    _locals = locals()

    exec_code_base = f"""from .test_result.services.general_service import *\nresp_result = root__get(passed_api_config)\nassert isinstance(resp_result, RootResponse)"""
    exec(exec_code_base, globals(), _locals)
    assert root_route.called

    exec_code_base = f"try:\n\tfrom .test_result import *\n\tresp_result = get_users_users_get(passed_api_config)\nexcept Exception as e:\n\tprint(e)\n\traise e"

    try:
        exec(exec_code_base, globals(), _locals)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        raise e

    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result, list)",
        globals(),
        _locals,
    )
    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result[0], User)",
        globals(),
        _locals,
    )
    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result[1], User)",
        globals(),
        _locals,
    )

    exec(exec_code_base, globals(), _locals)
    assert get_users_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = get_user_users__user_id__get(1,'test',passed_api_config)"

    exec(exec_code_base, globals(), _locals)

    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result, User)",
        globals(),
        _locals,
    )
    assert get_user_route.called
    assert (
        len(
            [
                (key, value)
                for key, value in get_user_route.calls[0][0].headers.raw
                if b"api-key" in key and b"test" in value
            ]
        )
        == 1
    )

    data = dict(
        id=1, username="user1", email="x@y.com", password="123456", is_active=True
    )

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = create_user_users_post(User(**{data}),passed_api_config)"

    exec(exec_code_base, globals(), _locals)

    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result, User)",
        globals(),
        _locals,
    )
    assert post_user_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = update_user_users__user_id__patch(1, User(**{data}), passed_api_config)"

    exec(exec_code_base, globals(), _locals)

    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result, User)",
        globals(),
        _locals,
    )
    assert update_user_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = delete_user_users__user_id__delete(1, passed_api_config)"

    exec(exec_code_base, globals(), _locals)

    assert delete_user_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = get_teams_teams_get(passed_api_config)"

    exec(exec_code_base, globals(), _locals)

    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result, list)",
        globals(),
        _locals,
    )
    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result[0], Team)",
        globals(),
        _locals,
    )
    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result[1], Team)",
        globals(),
        _locals,
    )
    assert get_teams_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = get_team_teams__team_id__get(1, passed_api_config)"

    exec(exec_code_base, globals(), _locals)
    assert get_team_route.called

    data = dict(
        id=1,
        name="team1",
        description="team1",
        is_active=True,
        created_at=None,
        updated_at=None,
    )

    exec_code_base = f"from .test_result.services.general_service import *\nfrom datetime import datetime\nresp_result = create_team_teams_post(Team(**{data}), passed_api_config)"

    exec(exec_code_base, globals(), _locals)
    assert post_team_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nfrom datetime import datetime\nresp_result = update_team_teams__team_id__patch(1, Team(**{data}), passed_api_config)"

    exec(exec_code_base, globals(), _locals)
    assert update_team_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = delete_team_teams__team_id__delete(1, passed_api_config)"

    exec(exec_code_base, globals(), _locals)

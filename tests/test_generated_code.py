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
        "from .test_result import *\nassert APIConfig.get_access_token() is None",
        globals(),
        _locals,
    )


@pytest.mark.parametrize(
    "library, use_orjson",
    [
        (HTTPLibrary.httpx, False),
        (HTTPLibrary.requests, False),
        (HTTPLibrary.httpx, True),
        (HTTPLibrary.requests, True),
        (HTTPLibrary.aiohttp, True),
        (HTTPLibrary.aiohttp, False),
    ],
)
@respx.mock
def test_generate_code(model_data_with_cleanup, library, use_orjson):
    generate_data(test_data_path, test_result_path, library, use_orjson=use_orjson)
    result = generator(model_data_with_cleanup, library_config_dict[library])

    # Testing root access
    _locals = locals()
    root_route = respx.get(f"{result.api_config.base_url}/").mock(
        return_value=Response(
            status_code=200, content=json.dumps({"message": "Hello World"})
        )
    )
    get_users_route = respx.get(f"{result.api_config.base_url}/users").mock(
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
    get_user_route = respx.get(f"{result.api_config.base_url}/users/{1}").mock(
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
    post_user_route = respx.post(f"{result.api_config.base_url}/users").mock(
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
    update_user_route = respx.patch(f"{result.api_config.base_url}/users/{1}").mock(
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
    delete_user_route = respx.delete(f"{result.api_config.base_url}/users/{1}").mock(
        return_value=Response(status_code=204, content=json.dumps(None))
    )

    get_teams_route = respx.get(f"{result.api_config.base_url}/teams").mock(
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

    get_team_route = respx.get(f"{result.api_config.base_url}/teams/{1}").mock(
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
    post_team_route = respx.post(f"{result.api_config.base_url}/teams").mock(
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

    update_team_route = respx.patch(f"{result.api_config.base_url}/teams/{1}").mock(
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

    delete_team_route = respx.delete(f"{result.api_config.base_url}/teams/{1}").mock(
        return_value=Response(status_code=204, content=json.dumps(None))
    )

    exec_code_base = f"""from .test_result.services.general_service import *\nresp_result = root__get()\nassert isinstance(resp_result, RootResponse)"""
    exec(exec_code_base, globals(), _locals)
    assert root_route.called

    exec_code_base = f"try:\n\tfrom .test_result import *\n\tresp_result = get_users_users_get()\nexcept Exception as e:\n\tprint(e)\n\traise e"

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

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = get_user_users__user_id__get(1)"

    exec(exec_code_base, globals(), _locals)

    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result, User)",
        globals(),
        _locals,
    )
    assert get_user_route.called

    data = dict(
        id=1, username="user1", email="x@y.com", password="123456", is_active=True
    )

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = create_user_users_post(User(**{data}))"

    exec(exec_code_base, globals(), _locals)

    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result, User)",
        globals(),
        _locals,
    )
    assert post_user_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = update_user_users__user_id__patch(1, User(**{data}))"

    exec(exec_code_base, globals(), _locals)

    exec(
        "from .test_result.services.general_service import *\nassert isinstance(resp_result, User)",
        globals(),
        _locals,
    )
    assert update_user_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = delete_user_users__user_id__delete(1)"

    exec(exec_code_base, globals(), _locals)

    assert delete_user_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = get_teams_teams_get()"

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

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = get_team_teams__team_id__get(1)"

    exec(exec_code_base, globals(), _locals)
    assert get_team_route.called

    data = dict(
        id=1,
        name="team1",
        description="team1",
        is_active=True,
        created_at="",
        updated_at="",
    )

    exec_code_base = f"from .test_result.services.general_service import *\nfrom datetime import datetime\nresp_result = create_team_teams_post(Team(**{data}))"

    exec(exec_code_base, globals(), _locals)
    assert post_team_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nfrom datetime import datetime\nresp_result = update_team_teams__team_id__patch(1, Team(**{data}))"

    exec(exec_code_base, globals(), _locals)
    assert update_team_route.called

    exec_code_base = f"from .test_result.services.general_service import *\nresp_result = delete_team_teams__team_id__delete(1)"

    exec(exec_code_base, globals(), _locals)

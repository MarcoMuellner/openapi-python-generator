# Getting started

## Pre requisits

As already denoted in [the quick start section](../quick_start.md), the first thing
you need to do is to actually install the generator. You can do so via pip
or any other package manager.

<div id="termynal" data-termynal data-termynal class="use-termynal" data-ty-typeDelay="40" data-ty-lineDelay="700">
    <span data-ty="input">pip install openapi-python-generator --upgrade</span>
    <span data-ty="progress"></span>
    <span data-ty>Successfully installed openapi-python-generator</span>
</div>

For this tutorial, we'll use the `test_api.json` file contained within the test
suite of the generator. It has the following structure:

<details>
<summary><b>test_api.json</b></summary>

```json
{
  "openapi": "3.0.2",
  "info": {
    "title": "openapi-python-generator test api",
    "description": "API Schema for openapi-python-generator test api",
    "version": "1.0.0",
    "x-logo": {
      "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
  },
  "paths": {
    "/": {
      "get": {
        "tags": [
          "general"
        ],
        "summary": "Root",
        "operationId": "root__get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/RootResponse"
                }
              }
            }
          }
        }
      }
    },
    "/users": {
      "get": {
        "tags": [
          "general"
        ],
        "summary": "Get Users",
        "operationId": "get_users_users_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "title": "Response Get Users Users Get",
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/User"
                  }
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "general"
        ],
        "summary": "Create User",
        "operationId": "create_user_users_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/User"
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/User"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/users/{user_id}": {
      "get": {
        "tags": [
          "general"
        ],
        "summary": "Get User",
        "operationId": "get_user_users__user_id__get",
        "parameters": [
          {
            "required": true,
            "schema": {
              "title": "User Id",
              "type": "integer"
            },
            "name": "user_id",
            "in": "path"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/User"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "general"
        ],
        "summary": "Delete User",
        "operationId": "delete_user_users__user_id__delete",
        "parameters": [
          {
            "required": true,
            "schema": {
              "title": "User Id",
              "type": "integer"
            },
            "name": "user_id",
            "in": "path"
          }
        ],
        "responses": {
          "204": {
            "description": "Successful Response"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "patch": {
        "tags": [
          "general"
        ],
        "summary": "Update User",
        "operationId": "update_user_users__user_id__patch",
        "parameters": [
          {
            "required": true,
            "schema": {
              "title": "User Id",
              "type": "integer"
            },
            "name": "user_id",
            "in": "path"
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/User"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/User"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/teams": {
      "get": {
        "tags": [
          "general"
        ],
        "summary": "Get Teams",
        "operationId": "get_teams_teams_get",
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "title": "Response Get Teams Teams Get",
                  "type": "array",
                  "items": {
                    "$ref": "#/components/schemas/Team"
                  }
                }
              }
            }
          }
        }
      },
      "post": {
        "tags": [
          "general"
        ],
        "summary": "Create Team",
        "operationId": "create_team_teams_post",
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Team"
              }
            }
          },
          "required": true
        },
        "responses": {
          "201": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Team"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    },
    "/teams/{team_id}": {
      "get": {
        "tags": [
          "general"
        ],
        "summary": "Get Team",
        "operationId": "get_team_teams__team_id__get",
        "parameters": [
          {
            "required": true,
            "schema": {
              "title": "Team Id",
              "type": "integer"
            },
            "name": "team_id",
            "in": "path"
          }
        ],
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Team"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "delete": {
        "tags": [
          "general"
        ],
        "summary": "Delete Team",
        "operationId": "delete_team_teams__team_id__delete",
        "parameters": [
          {
            "required": true,
            "schema": {
              "title": "Team Id",
              "type": "integer"
            },
            "name": "team_id",
            "in": "path"
          }
        ],
        "responses": {
          "204": {
            "description": "Successful Response"
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      },
      "patch": {
        "tags": [
          "general"
        ],
        "summary": "Update Team",
        "operationId": "update_team_teams__team_id__patch",
        "parameters": [
          {
            "required": true,
            "schema": {
              "title": "Team Id",
              "type": "integer"
            },
            "name": "team_id",
            "in": "path"
          }
        ],
        "requestBody": {
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/Team"
              }
            }
          },
          "required": true
        },
        "responses": {
          "200": {
            "description": "Successful Response",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Team"
                }
              }
            }
          },
          "422": {
            "description": "Validation Error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/HTTPValidationError"
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "HTTPValidationError": {
        "title": "HTTPValidationError",
        "type": "object",
        "properties": {
          "detail": {
            "title": "Detail",
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/ValidationError"
            }
          }
        }
      },
      "RootResponse": {
        "title": "RootResponse",
        "required": [
          "message"
        ],
        "type": "object",
        "properties": {
          "message": {
            "title": "Message",
            "type": "string"
          }
        }
      },
      "Team": {
        "title": "Team",
        "required": [
          "id",
          "name",
          "description"
        ],
        "type": "object",
        "properties": {
          "id": {
            "title": "Id",
            "type": "integer"
          },
          "name": {
            "title": "Name",
            "type": "string"
          },
          "description": {
            "title": "Description",
            "type": "string"
          },
          "is_active": {
            "title": "Is Active",
            "type": "boolean"
          },
          "created_at": {
            "title": "Created At",
            "type": "string",
            "format": "date-time"
          },
          "updated_at": {
            "title": "Updated At",
            "type": "string",
            "format": "date-time"
          },
          "users": {
            "title": "Users",
            "type": "array",
            "items": {
              "$ref": "#/components/schemas/User"
            }
          },
          "captain": {
            "$ref": "#/components/schemas/User"
          }
        }
      },
      "User": {
        "title": "User",
        "required": [
          "id",
          "username",
          "email",
          "password"
        ],
        "type": "object",
        "properties": {
          "id": {
            "title": "Id",
            "type": "integer"
          },
          "username": {
            "title": "Username",
            "type": "string"
          },
          "email": {
            "title": "Email",
            "type": "string"
          },
          "password": {
            "title": "Password",
            "type": "string"
          },
          "is_active": {
            "title": "Is Active",
            "type": "boolean"
          },
          "created_at": {
            "title": "Created At",
            "type": "string",
            "format": "date-time"
          }
        }
      },
      "EnumComponent": {
        "title": "EnumComponent",
        "enum": [
          "EnumValue1",
          "EnumValue2",
          "EnumValue3"
        ],
        "description": "An enumeration."
      },
      "ValidationError": {
        "title": "ValidationError",
        "required": [
          "loc",
          "msg",
          "type"
        ],
        "type": "object",
        "properties": {
          "loc": {
            "title": "Location",
            "type": "array",
            "items": {
              "anyOf": [
                {
                  "type": "string"
                },
                {
                  "type": "integer"
                }
              ]
            }
          },
          "msg": {
            "title": "Message",
            "type": "string"
          },
          "type": {
            "title": "Error Type",
            "type": "string"
          }
        }
      }
    }
  },
  "servers": [
    {
      "url": "http://localhost:8080"
    }
  ]
}
```
</details>

!!! tip "OpenAPI specification"

    Take a look at our short introduction to the
    [OpenAPI specification](../openapi-definition.md) if you need to look up
    what the specific nodes mean, or if you just need a refresher or some
    links for further information.

Lets run the generator on this file:

<div id="termynal" data-termynal data-termynal class="use-termynal" data-ty-typeDelay="40" data-ty-lineDelay="700">
    <span data-ty="input">openapi-python-generator https://raw.githubusercontent.com/MarcoMuellner/openapi-python-generator/main/tests/test_data/test_api.json testclient</span>
    <span data-ty>Generating data from https://raw.githubusercontent.com/MarcoMuellner/openapi-python-generator/main/tests/test_data/test_api.json</span>
</div>

This will result in the folder structure as denoted in the
[quick start](../quick_start.md) section. Lets take a deep dive on what
the generator created for us, starting with the models.

## The models module

The models module contains the generated models from the `Components` section
of the OpenAPI definition, each in their individual file. There are two
different types of models, currently supported by the generator:

- __pydantic models__
- __enums__

Both are valid structures in the OpenApi specification. The enumeration models
will always create mixin string classes, as for example in the `EnumContent.py`
file:

!!! note "EnumContent.py"

    ```py
    from enum import Enum


    class EnumComponent(str, Enum):

        enumvalue1 = "EnumValue1"
        enumvalue2 = "EnumValue2"
        enumvalue3 = "EnumValue3"

    ```

This is pretty straight forward, but what about the pydantic models? Lets
take a look at the `User.py` and the `Team.py` files:

=== "User.py"

    ``` py
    from typing import *

    from pydantic import BaseModel, Field


    class User(BaseModel):
    """
    User model

    """

    id: int = Field(alias="id")

    username: str = Field(alias="username")

    email: str = Field(alias="email")

    password: str = Field(alias="password")

    is_active: Optional[bool] = Field(alias="is_active", default=None)

    created_at: Optional[str] = Field(alias="created_at", default=None)

    ```

=== "Team.py"

    ``` py
    from typing import *

    from pydantic import BaseModel, Field

    from .User import User


    class Team(BaseModel):
    """
    Team model

    """

    id: int = Field(alias="id")

    name: str = Field(alias="name")

    description: str = Field(alias="description")

    is_active: Optional[bool] = Field(alias="is_active", default=None)

    created_at: Optional[str] = Field(alias="created_at", default=None)

    updated_at: Optional[str] = Field(alias="updated_at", default=None)

    users: Optional[List[User]] = Field(alias="users", default=None)

    captain: Optional[User] = Field(alias="captain", default=None)


    ```

If you are not familiar with the pydantic library, you can also check out
the [pydantic documentation](https://pydantic-docs.helpmanual.io/). Pydantic
is extremely useful, as it provides light weight in built validation and
type checking. We therefore can very easily represent the models and
their various properties (and requirements) through the models. For example,
the `created_at` property is optional (nullable) in the spec, and this is
therefore reflected in the model.

=== "test_api.json"
    ```json
    ...
    "required": [
          "id",
          "name",
          "description"
        ],
        ...
    "properties": {
        ...
        "created_at": {
                "title": "Created At",
                "type": "string",
                "format": "date-time"
              }
    ...
    ```

=== "Team.py"
    ``` py
    from typing import *

    from pydantic import BaseModel

    from .User import User


    class Team(BaseModel):
        ...
        created_at: Optional[str] = None
        ...

    ```

Hence, we can also directly use the json output from the service requests
and return these objects! (FastAPI does this too, but the other way round.)
The code also automatically converts to the proper python types, arrays and
Unions, as they are available by the OpenAPI specification. But lets take a look
at the services.

## The services module

The services module is the nitty gritty part of the generator. Depending on
the library you chose in the generator, the module will contain either one
or two submodules:

- `async_general_service.py` containing the async general service
- `general_service.py` containing the synchronous general service

Lets stop for a moment and take a look at that. The generator will create
a module for each individual `tag` from the OpenAPI specification:

!!! note "test_api.json"

    ```json
    ...
    "tags": [
          "general"
        ]
    ...
    ```

Therefore, if we add a second and third tag, the generator will create
the additional two - four modules.

The next thing is async support: You may want (depending on your usecase)
bot async and sync services. The generator will create both (for __httpx__),
only sync (for __requests__) or only async (for __aiohttp__) services.

=== "async_general_service.py"
    ``` py
    ...
    async def async_root__get() -> RootResponse:
        base_path = APIConfig().base_path
        path = f"/"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer { APIConfig().get_access_token() }",
        }
        query_params = {}

        with httpx.AsyncClient(base_url=base_path) as client:
            response = await client.request(
                method="get",
                url=path,
                headers=headers,
                params=query_params,
            )

        if response.status_code != 200:
            raise Exception(f" failed with status code: {response.status_code}")
        return RootResponse(**response.json())
    ...
    ```

=== "general_service.py"
    ``` py
    ...
    def root__get() -> RootResponse:
        base_path = APIConfig().base_path
        path = f"/"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer { APIConfig().get_access_token() }",
        }
        query_params = {}

        with httpx.Client(base_url=base_path) as client:
            response = client.request(
                method="get",
                url=path,
                headers=headers,
                params=query_params,
            )

        if response.status_code != 200:
            raise Exception(f" failed with status code: {response.status_code}")
        return RootResponse(**response.json())
    ...
    ```

While we are at the topic of looking at the individual functions, lets walk through the one above:

```py
...
def root__get() -> RootResponse:
...
```

All functions are fully annotated with the proper types, which provides the inspection of your IDE better insight
on what to provide to a given function and what to expect.

```py
...
path = f"/"
...
```

Paths are automatically created from the specification. No need to worry about that.

```py
...
headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer { APIConfig.get_access_token() }",
        }
query_params = {}
...
```

Authorization token is always passed to the Rest API, you will not need to worry about differentiating between the
calls. Query params are also automatically created, with the input parameters and depending on your spec (for
this root call no params are necessary)

```py
...
if response.status_code != 200:
    raise Exception(f" failed with status code: {response.status_code}")
return RootResponse(**response.json())
...
```

The generator will automatically raise an exception if a non-good status code was returned by the API, for
whatever reason. The "good" status code is also determined by the spec - and can be defined through your API.
For a post call for example, the spec will define a 201 status code as a good status code.

Lastly the code will automatically type check and convert the response to the appropriate type (in this case
`RootResponse`). This is really neat, because without doing much in the code, it automatically validates that
your API truly responds the way we expect it to respond, and gives you proper typing latter on in your code -
all thanks to the magic of [pydantic](https://pydantic-docs.helpmanual.io/).

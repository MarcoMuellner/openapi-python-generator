# A quick word about OpenAPI

_Note: This documentation is not intended to be a full introduction
to [OpenAPI](https://github.com/OAI/OpenAPI-Specification),
but rather a quick introduction into its workings, and how we can use it to generate Python code from an
OpenAPI 3.0.0 specification. Check their github repo and official documentation for more info._

## Introduction

The OpenAPI spec is an open and standardized format for describing RESTful APIs. This is especially useful, because
it provides a machine readable description of the API (in either JSON or YAML format), which can then be used
to do all kind of cool things with it. In our case, we'll try to automatically create a client for our API. Read
[this](https://oai.github.io/Documentation/specification.html) page on their documentation for a more in depth
description of the spec.

What we are interested in is specifically the [specifications document](https://spec.openapis.org/oas/v3.1.0), which
gives us an idea on what we can extract from the spec. At its minimum, the spec requires the following:

- The `openapi` field. This is the version of the spec.
- The `info` field. This is a dictionary containing information about the API (title, versions).
- The `paths` field. This is a dictionary containing the paths of the API (can be empty however).

Therefore a minimal spec would look like this:

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "My API",
    "version": "1.0.0"
  },
  "paths": {}
}
```

or in YAML:

```yaml
openapi: 3.1.0
info:
  title: A minimal OpenAPI document
  version: 0.0.1
paths: { } # No endpoints defined
```

We'll kepp to the json format for the rest of this documentation.

## The path dictionary

Of special interest is the `paths` dictionary. This dictionary contains all information necessay to describe
the given paths and operations of the API. Each `path` contains zero or more so called `operations`, which
describe the different HTTP methods that can be used on the given path. For more in depth info on
HTTP methods, see the [Modzilla web docs](https://developer.mozilla.org/de/docs/Web/HTTP/Methods). So, the structure
of any given path is as follows:

```json
{
  "/users": {
    "get": {
      ...
    },
    "post": {
      ...
    },
    "put": {
      ...
    }
  },
  "/teams": {
    "get": {
      ...
    },
    "post": {
      ...
    },
    "put": {
      ...
    }
  }
}
```

This is already pretty neat! We get a full list of all paths, and can do with them as we please. Now lets look
at these operations a bit more in detail.

## The operations

OpenAPI operations [have a ton of possible field](https://spec.openapis.org/oas/v3.1.0#operation-object). We don't
want to get into all of them, but rather take a look at the most important ones, 'parameters' and 'responses'

_Note: It makes sense to have more info on these operations than just these two fields. However, you will
very probably generate the `.json` from an existing API, and won't need to bother with the other fields much.
If you have to or want to, do take a look at the documentation above_

A potential operation could look something like this:

```json
{
  "get": {
    "summary": "Get a user",
    "description": "Get a user by id",
    "operationId": "getUser",
    "parameters": [
      {
        "name": "id",
        "in": "path",
        "description": "The id of the user",
        "required": true,
        "schema": {
          "type": "string"
        }
      }
    ],
    "responses": {
      "200": {
        "description": "A user",
        "content": {
          "application/json": {
            "schema": {
              "$ref": "#/components/schemas/User"
            }
          }
        }
      }
    }
  }
}
```

That is quite a lot of information! Lets walk through the fields step by step, starting with the `parameters` field.

```json
{
  "parameters": [
    {
      "name": "id", # The name of the parameter
      "in": "path", #The parameter is in the path or in the query string
      "description": "The id of the user", # A description of the parameter
      "required": true, #Wether the parameter must be present in the query or not
      "schema": {
        "type": "string" #The type of the parameter
      }
    }
  ]
}
```

__OpenAPI python generator__ will automatically take care of these parameters in the generated code, provide
args to pass (and default values if they aren't required), and will automatically add the parameters to where they
need to be (path or query string). Parameters can also refer to so called `References`, which we will cover
in the next subchapter.

Lets take a look at the `responses` field:

```json
{
  "200": { # The status code of the response
    "description": "A user", # Description of the response
    "content": { # The content and type of content
      "application/json": {
        "schema": {
          "$ref": "#/components/schemas/User" # A reference to a specific object in the spec
        }
      }
    }
  }
}
```
__OpenAPI python generator__ will take the first available `2xx` response code and use it as the "good" response code.
It will also raise a `HTTPException` for any other response code taken from the API. The `$ref` field is interesting,
it doesn't fit the normal `schema` definition of types. It refers to so called `Components` in the spec, which we
can also use to our advantage, by creating these components as pydantic models.

## Components

Last but not least, an OpenAPI spec can contain so called `Components`. These are dictionaries that contain
definitions to types that can be returned or input via body parameters to queries. For example, a user object
would look like this:

```json
{
  "components": {
    "schemas": {
      "User": {
        "type": "object",
        "properties": {
          "id": {
            "type": "string"
          },
          "name": {
            "type": "string"
          }
        }
      }
    }
  }
}
```

If you feel comfortable with the above, we can now move on to the actual generation of the code, and take a look
at the generator.

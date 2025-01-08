# API Reference

## CLI Interface

```console
$ openapi-python-generator <spec> <output_folder> [library]
```
Arguments:
```console
<spec>
    The OpenAPI spec to use. Either a URL or a local file.
<output_folder>
    The folder to output the generated code to.
```

Options:
```console
--library [httpx|requests|aiohttp]
                          HTTP library to use in the generation of the client.
                          Defaults to 'httpx'.

--env-token-name TEXT     Name of the environment variable that contains the token.
                          If set, code expects this environment variable and will
                          raise an error if not set.
                          Defaults to 'access_token'.

--use-orjson             Use the orjson library for JSON serialization. Enables
                         faster processing and better type support.
                         Defaults to False.

--custom-template-path TEXT
                         Custom template path to use. Allows overriding of the
                         built in templates.

--pydantic-version [v1|v2]
                         Pydantic version to use for generated models.
                         Defaults to 'v2'.

--formatter [black|none]
                         Option to choose which auto formatter is applied.
                         Defaults to 'black'.

--version                Show the version and exit.
-h, --help              Show this help message and exit.
```

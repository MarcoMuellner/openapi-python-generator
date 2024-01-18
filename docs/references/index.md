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
--library                  The library to use. Defaults to `httpx`.
--env-token-name           The name of the environment variable to use for the API key. Defaults to `access_token`.
--use-orjson               Use the `orjson` library for serialization. Defaults to `false`.
--custom-template-path     Use a custom template path to override the built in templates.
-h, --help                 Show this help message and exit.
```

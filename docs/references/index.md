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
--autoformat               Specifies which auto formattool to apply to the generated code. Defaults to `black`.
-h, --help                 Show this help message and exit.
```

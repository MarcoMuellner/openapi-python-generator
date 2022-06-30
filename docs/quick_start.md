# Quick start

Make sure you have the latest version of `openapi-python-generator` installed.

<div id="termynal" data-termynal data-termynal class="use-termynal" data-ty-typeDelay="40" data-ty-lineDelay="700">
    <span data-ty="input">pip install openapi-python-generator --upgrade</span>
    <span data-ty="progress"></span>
    <span data-ty>Successfully installed openapi-python-generator</span>
</div>

---

To call the generator, simply pass the OpenAPI spec (as a link or to a file), and an output folder. Optionally
you can also pass the library you would like to use.

<div id="termynal" data-termynal data-termynal class="use-termynal" data-ty-typeDelay="40" data-ty-lineDelay="700">
    <span data-ty="input">openapi-python-generator https://raw.githubusercontent.com/MarcoMuellner/openapi-python-generator/main/tests/test_data/test_api.json testclient</span>
    <span data-ty>Generating data from https://raw.githubusercontent.com/MarcoMuellner/openapi-python-generator/main/tests/test_data/test_api.json</span>
</div>

This will generate a folder called testclient, with the following structure (using the file above):

```
- models
    - __init__.py
    - HTTPValidationError.py
    - RootResponse.py
    - Team.py
    - User.py
    - ValidationError.py
    - EnumComponent.py
- services
    - __init__.py
    - async_general_service.py
    - general_service.py
- __init__.py
- api_config.py
```

To use it, simply import the module and call the functions:

```py
from testclient import root__get

root__get()  # Returns a RootResponse object
```

If you'd like more info, do check out our [Tutorial](tutorial/index.md) or the [API Reference](references/index.md).

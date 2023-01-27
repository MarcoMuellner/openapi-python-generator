# Openapi Python Generator

[![PyPI](https://img.shields.io/pypi/v/openapi-python-generator.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/openapi-python-generator.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/openapi-python-generator)][python version]
[![License](https://img.shields.io/pypi/l/openapi-python-generator)][license]

[![](https://img.shields.io/static/v1?label=documentation&message=enabled&color=<COLOR>)][documentation]
[![Tests](https://github.com/MarcoMuellner/openapi-python-generator/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/MarcoMuellner/openapi-python-generator/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/openapi-python-generator/
[status]: https://pypi.org/project/openapi-python-generator/
[python version]: https://pypi.org/project/openapi-python-generator
[documentation]: https://marcomuellner.github.io/openapi-python-generator/
[tests]: https://github.com/MarcoMuellner/openapi-python-generator/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/MarcoMuellner/openapi-python-generator
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

![](logo.png)

---
__Documentation:__ [here][documentation]

---

## Features

- __Ease of use__. Provide input, output and the library, and the generator will do the rest.
- __Type safety and type hinting.__ __OpenAPI python generator__ makes heavy use of pydantic models to provide type-safe data structures.
- __Support for multiple rest frameworks.__ __OpenAPI python generator__ currently supports the following:
    - [httpx](https://pypi.org/project/httpx/)
    - [requests](https://pypi.org/project/requests/)
    - [aiohttp](https://pypi.org/project/aiohttp/)
- __Async and sync code generation support__, depending on the framework. It will automatically create both for frameworks that support both.
- __Easily extendable using Jinja2 templates__. The code is designed to be easily extendable and should support even more languages and frameworks in the future.
- __Fully tested__. Every generated code is automatically tested against the OpenAPI spec and we have 100% coverage.
- __Usage as CLI or as library__.

## Requirements

- Python 3.7+

## Installation

You can install _Openapi Python Generator_ via [pip] from [PyPI]:

```console
$ pip install openapi-python-generator
```

## Usage

Please see the [Quick start page] for details.

## Roadmap

- Support for all commonly used http libraries in the python ecosystem (~~requests~~, urllib, ...)
- Support for multiple languages
- Support for multiple authentication schemes
- Support custom themes

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Openapi Python Generator_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

Special thanks to the peeps from [openapi-schema-pydantic](https://github.com/kuimono/openapi-schema-pydantic),
which already did a lot of the legwork by providing a pydantic schema for the OpenAPI 3.0.0+ specification.

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/MarcoMuellner/openapi-python-generator/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/MarcoMuellner/openapi-python-generator/blob/main/LICENSE
[contributor guide]: https://github.com/MarcoMuellner/openapi-python-generator/blob/main/CONTRIBUTING.md
[Quick start page]: https://marcomuellner.github.io/openapi-python-generator/quick_start/

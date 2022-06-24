# Openapi Python Generator

[![PyPI](https://img.shields.io/pypi/v/openapi-python-generator.svg)][pypi_]
[![Status](https://img.shields.io/pypi/status/openapi-python-generator.svg)][status]
[![Python Version](https://img.shields.io/pypi/pyversions/openapi-python-generator)][python version]
[![License](https://img.shields.io/pypi/l/openapi-python-generator)][license]

[![Read the documentation at https://openapi-python-generator.readthedocs.io/](https://img.shields.io/readthedocs/openapi-python-generator/latest.svg?label=Read%20the%20Docs)][read the docs]
[![Tests](https://github.com/MarcoMuellner/openapi-python-generator/workflows/Tests/badge.svg)][tests]
[![Codecov](https://codecov.io/gh/MarcoMuellner/openapi-python-generator/branch/main/graph/badge.svg)][codecov]

[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)][pre-commit]
[![Black](https://img.shields.io/badge/code%20style-black-000000.svg)][black]

[pypi_]: https://pypi.org/project/openapi-python-generator/
[status]: https://pypi.org/project/openapi-python-generator/
[python version]: https://pypi.org/project/openapi-python-generator
[read the docs]: https://openapi-python-generator.readthedocs.io/
[tests]: https://github.com/MarcoMuellner/openapi-python-generator/actions?workflow=Tests
[codecov]: https://app.codecov.io/gh/MarcoMuellner/openapi-python-generator
[pre-commit]: https://github.com/pre-commit/pre-commit
[black]: https://github.com/psf/black

## Features

- Easy code generation for OpenAPI 3.0.0+ APIs
- Async and Sync code generation support (with the help of [httpx](https://pypi.org/project/httpx/))])
- Typed services and models for your convinience
- Support for HttpBearer authentication
- Python only
- Usage as CLI tool or as a library

## Requirements

- Python 3.7+

## Installation

You can install _Openapi Python Generator_ via [pip] from [PyPI]:

```console
$ pip install openapi-python-generator
```

## Usage

Please see the [Command-line Reference] for details.

## Roadmap

- Support for all commonly used http libraries in the python ecosystem (requests, urllib, ...)
- Support for multiple languages
- Support for multiple authentication schemes

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

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/MarcoMuellner/openapi-python-generator/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/MarcoMuellner/openapi-python-generator/blob/main/LICENSE
[contributor guide]: https://github.com/MarcoMuellner/openapi-python-generator/blob/main/CONTRIBUTING.md
[command-line reference]: https://openapi-python-generator.readthedocs.io/en/latest/usage.html

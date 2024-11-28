# OpenAPI python generator

_OpenAPI python generator, a modern way to generate clients for OpenAPI 3.0.0+ APIs_

![](https://raw.githubusercontent.com/MarcoMuellner/openapi-python-generator/main/logo.png)

![Tests](https://github.com/MarcoMuellner/openapi-python-generator/workflows/Tests/badge.svg) ![Codecov](https://codecov.io/gh/MarcoMuellner/openapi-python-generator/branch/main/graph/badge.svg) ![PyPI](https://img.shields.io/pypi/v/openapi-python-generator.svg) ![Python Version](https://img.shields.io/pypi/pyversions/openapi-python-generator)
---

**Documentation**:

**Source**: [https://github.com/MarcoMuellner/openapi-python-generator](https://github.com/MarcoMuellner/openapi-python-generator)

---

OpenAPI python generator is a modern way to generate clients for OpenAPI 3.0.0+ APIs. It provides a full
Client, including pydantic models (providing type-safe data structures) and multiple supported frameworks.

The key features of the generator are:

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

Interested? Hop over to our Quickstart page, if you don't want to bother reading the docs, or if you just want to try it out.
If you want to get a more in depth guide, check out our Tutorials page. If you are interested in the OpenAPI spec,
go check out our OpenAPI Specification page.

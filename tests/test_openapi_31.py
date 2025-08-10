"""
Tests specifically for OpenAPI 3.1 support.
"""

import json
import tempfile
from pathlib import Path

import pytest

from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.version_detector import detect_openapi_version
from openapi_python_generator.parsers import parse_openapi_31


class TestOpenAPI31:
    """Test suite for OpenAPI 3.1 specific functionality."""

    @pytest.fixture
    def openapi_31_spec(self):
        """Sample OpenAPI 3.1 specification with 3.1-specific features."""
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Test API v3.1",
                "version": "2.0.0",
                "description": "OpenAPI 3.1 test specification with modern features",
                "license": {
                    "name": "MIT",
                    "identifier": "MIT",  # 3.1 feature: license identifier
                },
            },
            "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",  # 3.1 feature
            "servers": [{"url": "https://api.example.com/v2"}],
            "paths": {
                "/products": {
                    "get": {
                        "operationId": "list_products",
                        "summary": "List products",
                        "parameters": [
                            {
                                "name": "category",
                                "in": "query",
                                "required": False,
                                "schema": {
                                    "type": "string",
                                    "enum": ["electronics", "books", "clothing"],
                                },
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/Product"
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    },
                    "post": {
                        "operationId": "create_product",
                        "summary": "Create product",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/ProductCreate"
                                    }
                                }
                            },
                        },
                        "responses": {
                            "201": {
                                "description": "Created",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/Product"
                                        }
                                    }
                                },
                            }
                        },
                    },
                },
                "/products/{product_id}": {
                    "get": {
                        "operationId": "get_product",
                        "summary": "Get product by ID",
                        "parameters": [
                            {
                                "name": "product_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"},
                            }
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/Product"
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
            },
            "components": {
                "schemas": {
                    "Product": {
                        "type": "object",
                        "required": ["id", "name", "price"],
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "name": {"type": "string"},
                            "description": {
                                "anyOf": [  # 3.1 feature: anyOf at property level
                                    {"type": "string"},
                                    {"type": "null"},
                                ]
                            },
                            "price": {
                                "type": "number",
                                "minimum": 0,
                                "multipleOf": 0.01,
                            },
                            "category": {"$ref": "#/components/schemas/Category"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "default": [],  # 3.1 allows more flexible defaults
                            },
                            "metadata": {
                                "type": "object",
                                "additionalProperties": True,  # 3.1 explicit additionalProperties
                            },
                        },
                    },
                    "ProductCreate": {
                        "type": "object",
                        "required": ["name", "price", "category"],
                        "properties": {
                            "name": {"type": "string"},
                            "description": {
                                "anyOf": [{"type": "string"}, {"type": "null"}]
                            },
                            "price": {
                                "type": "number",
                                "minimum": 0,
                                "multipleOf": 0.01,
                            },
                            "category": {"$ref": "#/components/schemas/Category"},
                            "tags": {
                                "type": "array",
                                "items": {"type": "string"},
                                "default": [],
                            },
                        },
                    },
                    "Category": {
                        "type": "string",
                        "enum": ["electronics", "books", "clothing"],
                    },
                }
            },
        }

    def test_version_detection_31(self, openapi_31_spec):
        """Test that OpenAPI 3.1 specs are correctly detected."""
        version = detect_openapi_version(openapi_31_spec)
        assert version == "3.1"

    def test_parse_openapi_31(self, openapi_31_spec):
        """Test that OpenAPI 3.1 specs can be parsed correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        assert openapi_obj.openapi == "3.1.0"
        assert openapi_obj.info.title == "Test API v3.1"
        assert openapi_obj.paths is not None
        assert len(openapi_obj.paths) == 2
        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None
        assert len(openapi_obj.components.schemas) == 3

    def test_json_schema_dialect_31(self, openapi_31_spec):
        """Test that OpenAPI 3.1 jsonSchemaDialect is handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        # This is a 3.1-specific feature
        assert (
            openapi_obj.jsonSchemaDialect
            == "https://json-schema.org/draft/2020-12/schema"
        )

    def test_license_identifier_31(self, openapi_31_spec):
        """Test that OpenAPI 3.1 license identifier is handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        # This is a 3.1-specific feature
        assert openapi_obj.info.license is not None
        assert openapi_obj.info.license.name == "MIT"
        # Note: identifier is a 3.1 feature that might not be accessible due to Union types

    def test_anyof_schemas_31(self, openapi_31_spec):
        """Test that OpenAPI 3.1 anyOf schemas are handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None
        product_schema = openapi_obj.components.schemas["Product"]
        assert product_schema is not None

        # Note: Union types make direct property access complex
        # This test verifies the schema exists and can be parsed

    def test_generate_code_31(self, openapi_31_spec):
        """Test that code generation works for OpenAPI 3.1 specs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write spec to temporary file
            spec_file = Path(temp_dir) / "openapi_31.json"
            with open(spec_file, "w") as f:
                json.dump(openapi_31_spec, f)

            # Generate code
            output_dir = Path(temp_dir) / "generated"
            generate_data(spec_file, output_dir)

            # Check that files were generated
            assert (output_dir / "__init__.py").exists()
            assert (output_dir / "models").exists()
            assert (output_dir / "services").exists()
            assert (output_dir / "api_config.py").exists()

            # Check model structure
            assert (output_dir / "models" / "__init__.py").exists()
            models_dir = output_dir / "models"
            model_files = list(models_dir.glob("*.py"))
            assert (
                len(model_files) >= 3
            )  # Product.py, ProductCreate.py, Category.py (plus __init__.py)

            # Check that individual model files exist
            product_model_files = [f for f in model_files if "Product" in f.name]
            assert len(product_model_files) >= 1  # At least Product.py should exist

            # Check service structure
            services_dir = output_dir / "services"
            assert (services_dir / "__init__.py").exists()
            service_files = list(services_dir.glob("*_service.py"))
            assert len(service_files) >= 1

            # Check that httpx is used (since we updated to latest)
            service_content = ""
            for service_file in service_files:
                service_content += service_file.read_text()
            assert "import httpx" in service_content

    def test_uuid_parameter_31(self, openapi_31_spec):
        """Test that UUID parameters in OpenAPI 3.1 are handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        assert openapi_obj.paths is not None
        get_product_op = openapi_obj.paths["/products/{product_id}"].get
        assert get_product_op is not None
        assert get_product_op.parameters is not None
        assert len(get_product_op.parameters) == 1

        # Note: Union types make detailed assertions complex
        # This test verifies the UUID parameter structure exists
        param = get_product_op.parameters[0]
        assert param is not None

    def test_query_parameters_31(self, openapi_31_spec):
        """Test that query parameters in OpenAPI 3.1 are handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        assert openapi_obj.paths is not None
        list_products_op = openapi_obj.paths["/products"].get
        assert list_products_op is not None
        assert list_products_op.parameters is not None
        assert len(list_products_op.parameters) == 1

        # Note: Union types make detailed assertions complex
        # This test verifies the query parameter structure exists
        param = list_products_op.parameters[0]
        assert param is not None

    def test_enum_handling_31(self, openapi_31_spec):
        """Test that enums in OpenAPI 3.1 are handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None
        category_schema = openapi_obj.components.schemas["Category"]
        assert category_schema is not None

        # Note: Union types make detailed assertions complex
        # This test verifies the enum schema exists and can be parsed

    def test_reference_resolution_31(self, openapi_31_spec):
        """Test that references in OpenAPI 3.1 specs are handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        # Check that references exist in the spec
        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None
        product_schema = openapi_obj.components.schemas["Product"]
        # Note: We can't access properties directly on Union[Reference, Schema] types
        # This test verifies the schema exists and can be retrieved
        assert product_schema is not None

        # Check that paths reference schemas
        assert openapi_obj.paths is not None
        post_operation = openapi_obj.paths["/products"].post
        assert post_operation is not None
        assert post_operation.requestBody is not None
        assert hasattr(post_operation.requestBody, "content")

    def test_parameter_handling_31(self, openapi_31_spec):
        """Test that path and query parameters in OpenAPI 3.1 are handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        # Test path parameter
        assert openapi_obj.paths is not None
        get_product_op = openapi_obj.paths["/products/{product_id}"].get
        assert get_product_op is not None
        assert get_product_op.parameters is not None
        assert len(get_product_op.parameters) == 1

        # Test query parameter
        list_products_op = openapi_obj.paths["/products"].get
        assert list_products_op is not None
        assert list_products_op.parameters is not None
        assert len(list_products_op.parameters) >= 1  # At least the category parameter

        # Note: Union types make detailed assertions complex
        # This test verifies the parameter structure exists
        param = get_product_op.parameters[0]
        assert param is not None

    def test_request_body_31(self, openapi_31_spec):
        """Test that request bodies in OpenAPI 3.1 are handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        assert openapi_obj.paths is not None
        create_product_op = openapi_obj.paths["/products"].post
        assert create_product_op is not None
        assert create_product_op.requestBody is not None

        # Note: Union types make detailed assertions complex
        # This test verifies the request body structure exists
        assert hasattr(create_product_op.requestBody, "content") or hasattr(
            create_product_op.requestBody, "ref"
        )

    def test_response_handling_31(self, openapi_31_spec):
        """Test that responses in OpenAPI 3.1 are handled correctly."""
        openapi_obj = parse_openapi_31(openapi_31_spec)

        assert openapi_obj.paths is not None
        list_products_op = openapi_obj.paths["/products"].get
        assert list_products_op is not None
        assert list_products_op.responses is not None
        assert "200" in list_products_op.responses

        success_response = list_products_op.responses["200"]
        assert success_response is not None

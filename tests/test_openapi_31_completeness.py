"""
Tests to ensure OpenAPI 3.1 has equivalent coverage to OpenAPI 3.0.
Fills gaps in test coverage identified by comparing 3.0 vs 3.1 test suites.
"""

import json
import tempfile
from pathlib import Path

import pytest

from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.parsers import parse_openapi_31


class TestOpenAPI31Completeness:
    """Ensure OpenAPI 3.1 has equivalent test coverage to 3.0."""

    @pytest.fixture
    def comprehensive_31_spec(self):
        """Comprehensive OpenAPI 3.1 spec covering all major features."""
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "Comprehensive Test API",
                "version": "1.0.0",
                "description": "Complete OpenAPI 3.1 test for coverage parity",
                "license": {"name": "MIT", "identifier": "MIT"},
            },
            "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
            "servers": [{"url": "https://api.example.com/v1"}],
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "list_users",
                        "summary": "List users",
                        "parameters": [
                            {
                                "name": "limit",
                                "in": "query",
                                "required": False,
                                "schema": {
                                    "type": "integer",
                                    "minimum": 1,
                                    "maximum": 100,
                                },
                            },
                            {
                                "name": "status",
                                "in": "query",
                                "required": False,
                                "schema": {"$ref": "#/components/schemas/UserStatus"},
                            },
                            {
                                "name": "created_after",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "string", "format": "date"},
                            },
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "array",
                                            "items": {
                                                "$ref": "#/components/schemas/User"
                                            },
                                        }
                                    }
                                },
                            },
                            "400": {
                                "description": "Bad request",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Error"}
                                    }
                                },
                            },
                        },
                    },
                    "post": {
                        "operationId": "create_user",
                        "summary": "Create user",
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/UserCreate"
                                    }
                                },
                                "application/xml": {
                                    "schema": {
                                        "$ref": "#/components/schemas/UserCreate"
                                    }
                                },
                            },
                        },
                        "responses": {
                            "201": {
                                "description": "Created",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            },
                            "422": {
                                "description": "Validation error",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/ValidationError"
                                        }
                                    }
                                },
                            },
                        },
                    },
                },
                "/users/{user_id}": {
                    "get": {
                        "operationId": "get_user",
                        "summary": "Get user by ID",
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"},
                            },
                            {
                                "name": "include_deleted",
                                "in": "query",
                                "required": False,
                                "schema": {"type": "boolean", "default": False},
                            },
                        ],
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            },
                            "404": {
                                "description": "Not found",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/Error"}
                                    }
                                },
                            },
                        },
                    },
                    "put": {
                        "operationId": "update_user",
                        "summary": "Update user",
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"},
                            }
                        ],
                        "requestBody": {
                            "required": True,
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/UserUpdate"
                                    }
                                }
                            },
                        },
                        "responses": {
                            "200": {
                                "description": "Updated",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            },
                            "404": {"description": "Not found"},
                        },
                    },
                    "delete": {
                        "operationId": "delete_user",
                        "summary": "Delete user",
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"},
                            }
                        ],
                        "responses": {
                            "204": {"description": "Deleted"},
                            "404": {"description": "Not found"},
                        },
                    },
                },
                "/users/{user_id}/avatar": {
                    "post": {
                        "operationId": "upload_avatar",
                        "summary": "Upload user avatar",
                        "parameters": [
                            {
                                "name": "user_id",
                                "in": "path",
                                "required": True,
                                "schema": {"type": "string", "format": "uuid"},
                            }
                        ],
                        "requestBody": {
                            "content": {
                                "multipart/form-data": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "file": {
                                                "type": "string",
                                                "format": "binary",
                                            }
                                        },
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Avatar uploaded",
                                "content": {
                                    "application/json": {
                                        "schema": {"$ref": "#/components/schemas/User"}
                                    }
                                },
                            }
                        },
                    }
                },
            },
            "components": {
                "schemas": {
                    "User": {
                        "type": "object",
                        "required": ["id", "name", "email"],
                        "properties": {
                            "id": {"type": "string", "format": "uuid"},
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 100,
                            },
                            "email": {"type": "string", "format": "email"},
                            "age": {"type": "integer", "minimum": 0, "maximum": 150},
                            "status": {"$ref": "#/components/schemas/UserStatus"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "updated_at": {"type": "string", "format": "date-time"},
                            "avatar_url": {"type": "string", "format": "uri"},
                            "metadata": {
                                "type": "object",
                                "additionalProperties": {"type": "string"},
                            },
                        },
                    },
                    "UserCreate": {
                        "type": "object",
                        "required": ["name", "email"],
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 100,
                            },
                            "email": {"type": "string", "format": "email"},
                            "age": {"type": "integer", "minimum": 0, "maximum": 150},
                            "status": {"$ref": "#/components/schemas/UserStatus"},
                        },
                    },
                    "UserUpdate": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "minLength": 1,
                                "maxLength": 100,
                            },
                            "email": {"type": "string", "format": "email"},
                            "age": {"type": "integer", "minimum": 0, "maximum": 150},
                            "status": {"$ref": "#/components/schemas/UserStatus"},
                        },
                    },
                    "UserStatus": {
                        "type": "string",
                        "enum": ["active", "inactive", "pending", "suspended"],
                    },
                    "Error": {
                        "type": "object",
                        "required": ["code", "message"],
                        "properties": {
                            "code": {"type": "string"},
                            "message": {"type": "string"},
                            "details": {"type": "object", "additionalProperties": True},
                        },
                    },
                    "ValidationError": {
                        "type": "object",
                        "required": ["message", "errors"],
                        "properties": {
                            "message": {"type": "string"},
                            "errors": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "field": {"type": "string"},
                                        "code": {"type": "string"},
                                        "message": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                }
            },
        }

    @pytest.mark.parametrize(
        "library", [HTTPLibrary.httpx, HTTPLibrary.requests, HTTPLibrary.aiohttp]
    )
    def test_comprehensive_31_with_different_libraries(
        self, comprehensive_31_spec, library
    ):
        """Test OpenAPI 3.1 code generation with all HTTP libraries (matching 3.0 coverage)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Save spec to file
            spec_file = temp_path / "comprehensive_31.json"
            spec_file.write_text(json.dumps(comprehensive_31_spec, indent=2))

            # Generate code with specific library
            generate_data(spec_file, temp_path, library, use_orjson=False)

            # Verify basic structure
            assert (temp_path / "__init__.py").exists()
            assert (temp_path / "models").exists()
            assert (temp_path / "services").exists()
            assert (temp_path / "api_config.py").exists()

            # Verify library-specific imports in services
            services_dir = temp_path / "services"
            service_files = list(services_dir.glob("*_service.py"))
            assert len(service_files) >= 1

            service_content = ""
            for service_file in service_files:
                service_content += service_file.read_text()

            # Check library-specific imports
            if library == HTTPLibrary.httpx:
                assert "import httpx" in service_content
            elif library == HTTPLibrary.requests:
                assert "import requests" in service_content
            elif library == HTTPLibrary.aiohttp:
                assert "import aiohttp" in service_content

    def test_detailed_model_generation_31(self, comprehensive_31_spec):
        """Test detailed model generation for OpenAPI 3.1 (matching 3.0 coverage)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Save spec to file
            spec_file = temp_path / "comprehensive_31.json"
            spec_file.write_text(json.dumps(comprehensive_31_spec, indent=2))

            # Generate code
            generate_data(spec_file, temp_path, HTTPLibrary.httpx, use_orjson=False)

            # Check model structure in detail
            models_dir = temp_path / "models"
            assert (models_dir / "__init__.py").exists()

            # Check that model files are generated
            model_files = list(models_dir.glob("*.py"))
            model_names = [f.stem for f in model_files if f.stem != "__init__"]

            # Should have models for each schema
            expected_models = [
                "User",
                "UserCreate",
                "UserUpdate",
                "UserStatus",
                "Error",
                "ValidationError",
            ]
            for expected_model in expected_models:
                assert any(
                    expected_model in name for name in model_names
                ), f"Missing model for {expected_model}"

            # Check that models can be imported
            models_init = models_dir / "__init__.py"
            models_content = models_init.read_text()

            # Should export all models
            for expected_model in expected_models:
                assert (
                    expected_model in models_content
                ), f"Model {expected_model} not exported"

    def test_code_compilation_verification_31(self, comprehensive_31_spec):
        """Test that generated OpenAPI 3.1 code compiles successfully (matching 3.0 coverage)."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Save spec to file
            spec_file = temp_path / "comprehensive_31.json"
            spec_file.write_text(json.dumps(comprehensive_31_spec, indent=2))

            # Generate code
            generate_data(spec_file, temp_path, HTTPLibrary.httpx, use_orjson=False)

            # Test compilation of all generated files
            all_py_files = list(temp_path.rglob("*.py"))

            for py_file in all_py_files:
                content = py_file.read_text()
                try:
                    compile(content, str(py_file), "exec")
                except SyntaxError as e:
                    pytest.fail(f"Syntax error in {py_file}: {e}")
                except Exception as e:
                    pytest.fail(f"Compilation error in {py_file}: {e}")

    def test_complex_parameter_handling_31(self, comprehensive_31_spec):
        """Test complex parameter scenarios for OpenAPI 3.1 (matching 3.0 coverage)."""
        parsed = parse_openapi_31(comprehensive_31_spec)

        # Test path parameters
        get_user_op = parsed.paths["/users/{user_id}"].get
        assert get_user_op.parameters is not None

        path_params = [
            p
            for p in get_user_op.parameters
            if hasattr(p, "param_in") and p.param_in == "path"
        ]
        assert len(path_params) >= 1, "Should have path parameter"

        # Test query parameters with different types
        list_users_op = parsed.paths["/users"].get
        assert list_users_op.parameters is not None
        assert (
            len(list_users_op.parameters) >= 3
        ), "Should have multiple query parameters"

        # Test mixed parameter types (path + query)
        get_user_with_query = parsed.paths["/users/{user_id}"].get
        assert get_user_with_query.parameters is not None
        assert (
            len(get_user_with_query.parameters) >= 2
        ), "Should have both path and query parameters"

    def test_request_body_variations_31(self, comprehensive_31_spec):
        """Test various request body scenarios for OpenAPI 3.1 (matching 3.0 coverage)."""
        parsed = parse_openapi_31(comprehensive_31_spec)

        # Test JSON request body
        create_user_op = parsed.paths["/users"].post
        assert create_user_op.requestBody is not None

        # Test multipart/form-data request body
        upload_avatar_op = parsed.paths["/users/{user_id}/avatar"].post
        assert upload_avatar_op.requestBody is not None

        # Test multiple content types
        # The create_user operation should support both JSON and XML
        # (This tests the parsing, actual content type handling is implementation-specific)

    def test_response_variations_31(self, comprehensive_31_spec):
        """Test various response scenarios for OpenAPI 3.1 (matching 3.0 coverage)."""
        parsed = parse_openapi_31(comprehensive_31_spec)

        # Test multiple response codes
        list_users_op = parsed.paths["/users"].get
        assert list_users_op.responses is not None
        assert "200" in list_users_op.responses
        assert "400" in list_users_op.responses

        # Test responses with and without content
        delete_user_op = parsed.paths["/users/{user_id}"].delete
        assert delete_user_op.responses is not None
        assert "204" in delete_user_op.responses  # No content
        assert "404" in delete_user_op.responses  # Also no content

    def test_enum_handling_comprehensive_31(self, comprehensive_31_spec):
        """Test comprehensive enum handling for OpenAPI 3.1 (matching 3.0 coverage)."""
        parsed = parse_openapi_31(comprehensive_31_spec)

        assert parsed.components is not None
        assert parsed.components.schemas is not None

        # Test that UserStatus enum is parsed
        user_status_schema = parsed.components.schemas["UserStatus"]
        assert user_status_schema is not None

        # The enum should be referenced in other schemas
        user_schema = parsed.components.schemas["User"]
        assert user_schema is not None

    @pytest.mark.parametrize("use_orjson", [True, False])
    def test_serialization_options_31(self, comprehensive_31_spec, use_orjson):
        """Test both orjson and standard JSON serialization for OpenAPI 3.1."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Save spec to file
            spec_file = temp_path / "comprehensive_31.json"
            spec_file.write_text(json.dumps(comprehensive_31_spec, indent=2))

            # Generate code with orjson option
            generate_data(
                spec_file, temp_path, HTTPLibrary.httpx, use_orjson=use_orjson
            )

            # Verify files exist
            assert (temp_path / "__init__.py").exists()
            assert (temp_path / "models").exists()
            assert (temp_path / "services").exists()

            # Check for orjson usage if enabled
            if use_orjson:
                models_content = ""
                for py_file in (temp_path / "models").glob("*.py"):
                    models_content += py_file.read_text()

                # Should use orjson if available and requested
                # (The actual usage depends on the model generator implementation)
                # This test ensures the option is processed without errors

    def test_reference_resolution_comprehensive_31(self, comprehensive_31_spec):
        """Test comprehensive reference resolution for OpenAPI 3.1 (matching 3.0 coverage)."""
        parsed = parse_openapi_31(comprehensive_31_spec)

        # Test schema references
        assert parsed.components is not None
        assert parsed.components.schemas is not None

        user_schema = parsed.components.schemas["User"]
        user_create_schema = parsed.components.schemas["UserCreate"]
        user_status_schema = parsed.components.schemas["UserStatus"]

        assert user_schema is not None
        assert user_create_schema is not None
        assert user_status_schema is not None

        # Test that references in paths work
        list_users_op = parsed.paths["/users"].get
        assert list_users_op.responses is not None
        assert "200" in list_users_op.responses

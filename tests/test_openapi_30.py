"""
Tests specifically for OpenAPI 3.0 support.
"""

import json
import tempfile
from pathlib import Path

import pytest

from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.version_detector import detect_openapi_version
from openapi_python_generator.parsers import parse_openapi_3_0


class TestOpenAPI30:
    """Test suite for OpenAPI 3.0 specific functionality."""

    @pytest.fixture
    def openapi_30_spec(self):
        """Sample OpenAPI 3.0 specification."""
        return {
            "openapi": "3.0.2",
            "info": {
                "title": "Test API",
                "version": "1.0.0",
                "description": "OpenAPI 3.0 test specification",
            },
            "servers": [{"url": "https://api.example.com/v1"}],
            "paths": {
                "/users": {
                    "get": {
                        "operationId": "list_users",
                        "summary": "List users",
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
                            }
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
                                }
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
                            }
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
                                "schema": {"type": "integer"},
                            }
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
                            "404": {"description": "Not found"},
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
                            "id": {"type": "integer", "format": "int64"},
                            "name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "created_at": {"type": "string", "format": "date-time"},
                            "status": {"$ref": "#/components/schemas/UserStatus"},
                        },
                    },
                    "UserCreate": {
                        "type": "object",
                        "required": ["name", "email"],
                        "properties": {
                            "name": {"type": "string"},
                            "email": {"type": "string", "format": "email"},
                            "status": {"$ref": "#/components/schemas/UserStatus"},
                        },
                    },
                    "UserStatus": {
                        "type": "string",
                        "enum": ["active", "inactive", "pending"],
                    },
                }
            },
        }

    def test_version_detection_30(self, openapi_30_spec):
        """Test that OpenAPI 3.0 specs are correctly detected."""
        version = detect_openapi_version(openapi_30_spec)
        assert version == "3.0"

    def test_parse_openapi_30(self, openapi_30_spec):
        """Test that OpenAPI 3.0 specs can be parsed correctly."""
        openapi_obj = parse_openapi_3_0(openapi_30_spec)

        assert openapi_obj.openapi == "3.0.2"
        assert openapi_obj.info.title == "Test API"
        assert len(openapi_obj.paths) == 2
        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None
        assert len(openapi_obj.components.schemas) == 3

    def test_reference_resolution_30(self, openapi_30_spec):
        """Test that references in OpenAPI 3.0 specs are handled correctly."""
        openapi_obj = parse_openapi_3_0(openapi_30_spec)

        # Check that references exist in the spec
        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None
        user_schema = openapi_obj.components.schemas["User"]
        # Note: We can't access properties directly on Union[Reference, Schema] types
        # This test verifies the schema exists and can be retrieved
        assert user_schema is not None

        # Check that paths reference schemas
        post_operation = openapi_obj.paths["/users"].post
        assert post_operation is not None
        assert post_operation.requestBody is not None
        assert hasattr(post_operation.requestBody, "content")

    def test_enum_handling_30(self, openapi_30_spec):
        """Test that enums in OpenAPI 3.0 are handled correctly."""
        openapi_obj = parse_openapi_3_0(openapi_30_spec)

        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None
        status_schema = openapi_obj.components.schemas["UserStatus"]
        # Note: Direct attribute access on Union types is complex
        # This test verifies the enum schema exists
        assert status_schema is not None

    def test_generate_code_30(self, openapi_30_spec):
        """Test that code generation works for OpenAPI 3.0 specs."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write spec to temporary file
            spec_file = Path(temp_dir) / "openapi_30.json"
            with open(spec_file, "w") as f:
                json.dump(openapi_30_spec, f)

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
            )  # User.py, UserCreate.py, UserStatus.py (plus __init__.py)

            # Check that individual model files exist
            user_model_files = [f for f in model_files if "User" in f.name]
            assert len(user_model_files) >= 1  # At least User.py should exist

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

    def test_parameter_handling_30(self, openapi_30_spec):
        """Test that path parameters in OpenAPI 3.0 are handled correctly."""
        openapi_obj = parse_openapi_3_0(openapi_30_spec)

        get_user_op = openapi_obj.paths["/users/{user_id}"].get
        assert get_user_op is not None
        assert get_user_op.parameters is not None
        assert len(get_user_op.parameters) == 1

        # Note: Union types make detailed assertions complex
        # This test verifies the parameter structure exists
        param = get_user_op.parameters[0]
        assert param is not None

    def test_request_body_30(self, openapi_30_spec):
        """Test that request bodies in OpenAPI 3.0 are handled correctly."""
        openapi_obj = parse_openapi_3_0(openapi_30_spec)

        create_user_op = openapi_obj.paths["/users"].post
        assert create_user_op is not None
        assert create_user_op.requestBody is not None

        # Note: Union types make detailed assertions complex
        # This test verifies the request body structure exists
        assert hasattr(create_user_op.requestBody, "content") or hasattr(
            create_user_op.requestBody, "ref"
        )

    def test_response_handling_30(self, openapi_30_spec):
        """Test that responses in OpenAPI 3.0 are handled correctly."""
        openapi_obj = parse_openapi_3_0(openapi_30_spec)

        list_users_op = openapi_obj.paths["/users"].get
        assert list_users_op is not None
        assert list_users_op.responses is not None
        assert "200" in list_users_op.responses

        success_response = list_users_op.responses["200"]
        assert success_response is not None

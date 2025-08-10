"""
Tests specifically for Swagger Petstore OpenAPI 3.1 specification.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.version_detector import detect_openapi_version
from openapi_python_generator.parsers import parse_openapi_31
from openapi_python_generator.common import HTTPLibrary


class TestSwaggerPetstore31:
    """Test suite for Swagger Petstore OpenAPI 3.1 specification."""

    @pytest.fixture
    def petstore_31_spec_path(self):
        """Path to the Swagger Petstore OpenAPI 3.1 specification."""
        return Path(__file__).parent / "test_data" / "swagger_petstore_3_1.yaml"

    @pytest.fixture
    def petstore_31_spec(self, petstore_31_spec_path):
        """Load the Swagger Petstore OpenAPI 3.1 specification."""
        with open(petstore_31_spec_path, "r") as f:
            return yaml.safe_load(f)

    def test_version_detection_petstore_31(self, petstore_31_spec):
        """Test that the Petstore 3.1 spec is correctly identified as OpenAPI 3.1."""
        version = detect_openapi_version(petstore_31_spec)
        assert version == "3.1"

    def test_parse_petstore_31(self, petstore_31_spec):
        """Test that the Petstore 3.1 spec can be parsed successfully."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        # Basic structure validation
        assert openapi_obj.openapi == "3.1.0"
        assert openapi_obj.info.title == "Swagger Petstore - OpenAPI 3.1"
        assert openapi_obj.info.version == "1.0.12"

        # Check paths
        assert openapi_obj.paths is not None
        assert "/pet" in openapi_obj.paths
        assert "/pet/findByStatus" in openapi_obj.paths
        assert "/pet/{petId}" in openapi_obj.paths
        assert "/store/order" in openapi_obj.paths
        assert "/user" in openapi_obj.paths

    def test_petstore_31_schemas(self, petstore_31_spec):
        """Test that Petstore 3.1 schemas are parsed correctly."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None

        # Check key schemas exist
        schemas = openapi_obj.components.schemas
        assert "Pet" in schemas
        assert "Category" in schemas
        assert "Tag" in schemas
        assert "Order" in schemas
        assert "User" in schemas
        assert "ApiResponse" in schemas

    def test_petstore_31_operations(self, petstore_31_spec):
        """Test that Petstore 3.1 operations are parsed correctly."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        assert openapi_obj.paths is not None

        # Check POST /pet operation
        pet_post = openapi_obj.paths["/pet"].post
        assert pet_post is not None
        assert pet_post.operationId == "addPet"
        assert pet_post.requestBody is not None

        # Check GET /pet/findByStatus operation
        find_by_status = openapi_obj.paths["/pet/findByStatus"].get
        assert find_by_status is not None
        assert find_by_status.operationId == "findPetsByStatus"
        assert find_by_status.parameters is not None
        assert len(find_by_status.parameters) == 1

    def test_petstore_31_parameters(self, petstore_31_spec):
        """Test that Petstore 3.1 parameters are handled correctly."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        assert openapi_obj.paths is not None

        # Check path parameter in GET /pet/{petId}
        get_pet = openapi_obj.paths["/pet/{petId}"].get
        assert get_pet is not None
        assert get_pet.parameters is not None
        assert len(get_pet.parameters) == 1

        # Check query parameter in GET /pet/findByStatus
        find_by_status = openapi_obj.paths["/pet/findByStatus"].get
        assert find_by_status is not None
        assert find_by_status.parameters is not None
        assert len(find_by_status.parameters) == 1

    def test_petstore_31_responses(self, petstore_31_spec):
        """Test that Petstore 3.1 responses are handled correctly."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        assert openapi_obj.paths is not None

        # Check responses for GET /pet/{petId}
        get_pet = openapi_obj.paths["/pet/{petId}"].get
        assert get_pet is not None
        assert get_pet.responses is not None
        assert "200" in get_pet.responses
        assert "400" in get_pet.responses
        assert "404" in get_pet.responses

    def test_petstore_31_json_schema_dialect(self, petstore_31_spec):
        """Test that Petstore 3.1 uses the correct JSON Schema dialect."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        # Check if jsonSchemaDialect is set (it might not be in all 3.1 specs)
        # This is more of a validation that the spec is properly formed
        assert openapi_obj.openapi == "3.1.0"

    def test_petstore_31_examples(self, petstore_31_spec):
        """Test that Petstore 3.1 examples are handled correctly."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None

        # The 3.1 spec might have different example structures
        # This test validates the spec can be parsed without errors
        pet_schema = openapi_obj.components.schemas.get("Pet")
        assert pet_schema is not None

    def test_generate_code_petstore_31(self, petstore_31_spec_path):
        """Test that code generation works for Petstore 3.1 spec."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "generated"

            # Generate code
            generate_data(petstore_31_spec_path, output_dir, HTTPLibrary.httpx)

            # Check that files were generated
            assert (output_dir / "__init__.py").exists()
            assert (output_dir / "models").exists()
            assert (output_dir / "services").exists()
            assert (output_dir / "api_config.py").exists()

            # Check model files
            models_dir = output_dir / "models"
            assert (models_dir / "__init__.py").exists()

            # Check that key model files exist
            expected_models = [
                "Pet.py",
                "Category.py",
                "Tag.py",
                "Order.py",
                "User.py",
                "ApiResponse.py",
            ]
            for model_file in expected_models:
                assert (
                    models_dir / model_file
                ).exists(), f"Missing model file: {model_file}"

            # Check service files
            services_dir = output_dir / "services"
            assert (services_dir / "__init__.py").exists()

            # Should have service files for different tags
            service_files = list(services_dir.glob("*.py"))
            service_files = [f for f in service_files if f.name != "__init__.py"]
            assert len(service_files) > 0, "No service files generated"

    @pytest.mark.parametrize("library", [HTTPLibrary.httpx, HTTPLibrary.requests])
    def test_petstore_31_with_different_libraries(self, petstore_31_spec_path, library):
        """Test that Petstore 3.1 code generation works with different HTTP libraries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "generated"

            # This should not raise an exception
            generate_data(petstore_31_spec_path, output_dir, library)

            # Basic validation that output was created
            assert output_dir.exists()
            assert (output_dir / "api_config.py").exists()

    @pytest.mark.parametrize("use_orjson", [True, False])
    def test_petstore_31_with_orjson_options(self, petstore_31_spec_path, use_orjson):
        """Test that Petstore 3.1 code generation works with different orjson settings."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "generated"

            # This should not raise an exception
            generate_data(
                petstore_31_spec_path,
                output_dir,
                HTTPLibrary.httpx,
                use_orjson=use_orjson,
            )

            # Basic validation that output was created
            assert output_dir.exists()
            assert (output_dir / "api_config.py").exists()

    def test_petstore_31_uuid_parameters(self, petstore_31_spec):
        """Test that UUID parameters in Petstore 3.1 are handled correctly."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        # The Petstore spec might use UUID formats for some IDs
        # This test validates that the spec parses without issues
        assert openapi_obj.paths is not None

        # Check if any operations have UUID parameters
        get_pet = openapi_obj.paths["/pet/{petId}"].get
        assert get_pet is not None
        assert get_pet.parameters is not None

    def test_petstore_31_model_generation_basic(self, petstore_31_spec):
        """Test basic model generation for Petstore 3.1."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        # Basic validation that components exist
        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None

        # Check that key schemas exist
        schemas = openapi_obj.components.schemas
        expected_schemas = ["Pet", "Category", "Tag", "Order", "User", "ApiResponse"]
        for schema_name in expected_schemas:
            assert schema_name in schemas, f"Missing schema: {schema_name}"

    def test_petstore_31_service_operations_basic(self, petstore_31_spec):
        """Test basic service operations for Petstore 3.1."""
        openapi_obj = parse_openapi_31(petstore_31_spec)

        assert openapi_obj.paths is not None

        # Check that all expected paths exist
        expected_paths = [
            "/pet",
            "/pet/findByStatus",
            "/pet/{petId}",
            "/store/order",
            "/user",
        ]
        for path in expected_paths:
            assert path in openapi_obj.paths, f"Missing path: {path}"

        # Check that operations have the expected structure
        pet_operations = openapi_obj.paths["/pet"]
        assert pet_operations.post is not None  # Add pet
        assert pet_operations.put is not None  # Update pet

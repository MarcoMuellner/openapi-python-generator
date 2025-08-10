"""
Tests specifically for Swagger Petstore OpenAPI 3.0 specification.
"""

import tempfile
from pathlib import Path

import pytest
import yaml

from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.version_detector import detect_openapi_version
from openapi_python_generator.parsers import parse_openapi_30
from openapi_python_generator.common import HTTPLibrary


class TestSwaggerPetstore30:
    """Test suite for Swagger Petstore OpenAPI 3.0 specification."""

    @pytest.fixture
    def petstore_30_spec_path(self):
        """Path to the Swagger Petstore OpenAPI 3.0 specification."""
        return Path(__file__).parent / "test_data" / "swagger_petstore_3_0_4.yaml"

    @pytest.fixture
    def petstore_30_spec(self, petstore_30_spec_path):
        """Load the Swagger Petstore OpenAPI 3.0 specification."""
        with open(petstore_30_spec_path, "r") as f:
            return yaml.safe_load(f)

    def test_version_detection_petstore_30(self, petstore_30_spec):
        """Test that the Petstore 3.0 spec is correctly identified as OpenAPI 3.0."""
        version = detect_openapi_version(petstore_30_spec)
        assert version == "3.0"

    def test_parse_petstore_30(self, petstore_30_spec):
        """Test that the Petstore 3.0 spec can be parsed successfully."""
        openapi_obj = parse_openapi_30(petstore_30_spec)

        # Basic structure validation
        assert openapi_obj.openapi == "3.0.4"
        assert openapi_obj.info.title == "Swagger Petstore - OpenAPI 3.0"
        assert openapi_obj.info.version == "1.0.12"

        # Check paths
        assert openapi_obj.paths is not None
        assert "/pet" in openapi_obj.paths
        assert "/pet/findByStatus" in openapi_obj.paths
        assert "/pet/{petId}" in openapi_obj.paths
        assert "/store/order" in openapi_obj.paths
        assert "/user" in openapi_obj.paths

    def test_petstore_30_schemas(self, petstore_30_spec):
        """Test that Petstore 3.0 schemas are parsed correctly."""
        openapi_obj = parse_openapi_30(petstore_30_spec)

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

    def test_petstore_30_operations(self, petstore_30_spec):
        """Test that Petstore 3.0 operations are parsed correctly."""
        openapi_obj = parse_openapi_30(petstore_30_spec)

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

    def test_petstore_30_parameters(self, petstore_30_spec):
        """Test that Petstore 3.0 parameters are handled correctly."""
        openapi_obj = parse_openapi_30(petstore_30_spec)

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

    def test_petstore_30_responses(self, petstore_30_spec):
        """Test that Petstore 3.0 responses are handled correctly."""
        openapi_obj = parse_openapi_30(petstore_30_spec)

        assert openapi_obj.paths is not None

        # Check responses for GET /pet/{petId}
        get_pet = openapi_obj.paths["/pet/{petId}"].get
        assert get_pet is not None
        assert get_pet.responses is not None
        assert "200" in get_pet.responses
        assert "400" in get_pet.responses
        assert "404" in get_pet.responses

    def test_generate_code_petstore_30(self, petstore_30_spec_path):
        """Test that code generation works for Petstore 3.0 spec."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "generated"

            # Generate code
            generate_data(petstore_30_spec_path, output_dir, HTTPLibrary.httpx)

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
    def test_petstore_30_with_different_libraries(self, petstore_30_spec_path, library):
        """Test that Petstore 3.0 code generation works with different HTTP libraries."""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir) / "generated"

            # This should not raise an exception
            generate_data(petstore_30_spec_path, output_dir, library)

            # Basic validation that output was created
            assert output_dir.exists()
            assert (output_dir / "api_config.py").exists()

    def test_petstore_30_model_generation(self, petstore_30_spec):
        """Test that model generation works correctly for Petstore 3.0."""
        openapi_obj = parse_openapi_30(petstore_30_spec)

        # Basic validation that components exist
        assert openapi_obj.components is not None
        assert openapi_obj.components.schemas is not None

        # Check that key models exist
        schemas = openapi_obj.components.schemas
        expected_models = ["Pet", "Category", "Tag", "Order", "User", "ApiResponse"]
        for expected_model in expected_models:
            assert expected_model in schemas, f"Missing model: {expected_model}"

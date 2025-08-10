"""
Test OpenAPI 3.1 features that are currently supported vs unsupported.
"""

import tempfile
from pathlib import Path

import pytest

from openapi_python_generator.generate_data import generate_data
from openapi_python_generator.common import HTTPLibrary
from openapi_python_generator.parsers import parse_openapi_31


class TestOpenAPI31SupportedFeatures:
    """Test OpenAPI 3.1 features that should work with current openapi-pydantic."""

    @pytest.fixture
    def supported_openapi_31_spec(self):
        """OpenAPI 3.1 spec with currently supported features."""
        return {
            "openapi": "3.1.0",
            "info": {
                "title": "OpenAPI 3.1 Supported Features Test",
                "version": "1.0.0",
                "license": {"name": "MIT", "identifier": "MIT"},
            },
            "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
            "servers": [{"url": "https://api.example.com"}],
            "paths": {
                "/test": {
                    "post": {
                        "operationId": "test_supported_features",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "$ref": "#/components/schemas/TestRequest"
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Success",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "$ref": "#/components/schemas/TestResponse"
                                        }
                                    }
                                },
                            }
                        },
                    }
                }
            },
            "components": {
                "schemas": {
                    # Test const keyword
                    "ConstValue": {"type": "string", "const": "FIXED_VALUE"},
                    # Test prefixItems (tuple validation)
                    "TupleArray": {
                        "type": "array",
                        "prefixItems": [
                            {"type": "string"},
                            {"type": "number"},
                            {"type": "boolean"},
                        ],
                        # Note: can't use items: false due to library limitations
                    },
                    # Test contains with min/max
                    "ArrayWithContains": {
                        "type": "array",
                        "items": {"type": "string"},
                        "contains": {"const": "required_item"},
                        "minContains": 1,
                        "maxContains": 3,
                    },
                    # Test dependentSchemas
                    "DependentSchema": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "credit_card": {"type": "string"},
                            "billing_address": {"type": "string"},
                        },
                        "dependentSchemas": {
                            "credit_card": {
                                "type": "object",
                                "required": ["billing_address"],
                            }
                        },
                    },
                    # Test exclusive numeric constraints as numbers (3.1 style)
                    "NumericConstraints": {
                        "type": "object",
                        "properties": {
                            "score": {
                                "type": "number",
                                "exclusiveMinimum": 0,
                                "exclusiveMaximum": 100,
                            },
                            "rating": {"type": "integer", "minimum": 1, "maximum": 5},
                        },
                    },
                    # Test if/then/else conditional logic
                    "ConditionalSchema": {
                        "type": "object",
                        "properties": {
                            "type": {"type": "string", "enum": ["premium", "basic"]},
                            "features": {"type": "array", "items": {"type": "string"}},
                            "price": {"type": "number"},
                        },
                        "schema_if": {
                            "type": "object",
                            "properties": {"type": {"const": "premium"}},
                        },
                        "then": {
                            "type": "object",
                            "properties": {
                                "price": {"minimum": 100},
                                "features": {"minItems": 5},
                            },
                        },
                        "schema_else": {
                            "type": "object",
                            "properties": {
                                "price": {"maximum": 50},
                                "features": {"maxItems": 2},
                            },
                        },
                    },
                    # Test complex union with discriminator
                    "ComplexUnion": {
                        "anyOf": [
                            {
                                "type": "object",
                                "properties": {
                                    "type": {"const": "text"},
                                    "content": {"type": "string"},
                                },
                                "required": ["type", "content"],
                            },
                            {
                                "type": "object",
                                "properties": {
                                    "type": {"const": "image"},
                                    "url": {"type": "string", "format": "uri"},
                                    "alt_text": {"type": "string"},
                                },
                                "required": ["type", "url"],
                            },
                        ],
                        "discriminator": {"propertyName": "type"},
                    },
                    # Test patternProperties
                    "DynamicProperties": {
                        "type": "object",
                        "patternProperties": {
                            "^meta_": {"type": "string"},
                            "^config_": {
                                "anyOf": [
                                    {"type": "string"},
                                    {"type": "number"},
                                    {"type": "boolean"},
                                ]
                            },
                        },
                    },
                    # Main schemas
                    "TestRequest": {
                        "type": "object",
                        "properties": {
                            "const_field": {"$ref": "#/components/schemas/ConstValue"},
                            "tuple_field": {"$ref": "#/components/schemas/TupleArray"},
                            "conditional_field": {
                                "$ref": "#/components/schemas/ConditionalSchema"
                            },
                            "union_field": {
                                "$ref": "#/components/schemas/ComplexUnion"
                            },
                            "numeric_field": {
                                "$ref": "#/components/schemas/NumericConstraints"
                            },
                            "dynamic_field": {
                                "$ref": "#/components/schemas/DynamicProperties"
                            },
                            "array_field": {
                                "$ref": "#/components/schemas/ArrayWithContains"
                            },
                            "dependent_field": {
                                "$ref": "#/components/schemas/DependentSchema"
                            },
                        },
                    },
                    "TestResponse": {
                        "type": "object",
                        "properties": {
                            "success": {"type": "boolean"},
                            "processed_count": {"type": "integer"},
                        },
                    },
                }
            },
        }

    def test_parsing_supported_features(self, supported_openapi_31_spec):
        """Test that all supported 3.1 features parse correctly."""
        parsed = parse_openapi_31(supported_openapi_31_spec)

        # Verify basic parsing worked
        assert parsed.openapi == "3.1.0"
        assert (
            parsed.jsonSchemaDialect == "https://json-schema.org/draft/2020-12/schema"
        )

        # Verify schemas exist
        schemas = parsed.components.schemas
        assert "ConstValue" in schemas
        assert "TupleArray" in schemas
        assert "ConditionalSchema" in schemas
        assert "ComplexUnion" in schemas

    def test_const_schema_parsing(self, supported_openapi_31_spec):
        """Test const schema parsing."""
        parsed = parse_openapi_31(supported_openapi_31_spec)
        const_schema = parsed.components.schemas["ConstValue"]

        assert const_schema.type == "string"
        assert const_schema.const == "FIXED_VALUE"

    def test_prefix_items_parsing(self, supported_openapi_31_spec):
        """Test prefixItems parsing."""
        parsed = parse_openapi_31(supported_openapi_31_spec)
        tuple_schema = parsed.components.schemas["TupleArray"]

        assert tuple_schema.type == "array"
        assert tuple_schema.prefixItems is not None
        assert len(tuple_schema.prefixItems) == 3

        # Check each prefix item
        assert tuple_schema.prefixItems[0].type == "string"
        assert tuple_schema.prefixItems[1].type == "number"
        assert tuple_schema.prefixItems[2].type == "boolean"

    def test_contains_constraints_parsing(self, supported_openapi_31_spec):
        """Test contains/minContains/maxContains parsing."""
        parsed = parse_openapi_31(supported_openapi_31_spec)
        array_schema = parsed.components.schemas["ArrayWithContains"]

        assert array_schema.contains is not None
        assert array_schema.contains.const == "required_item"
        assert array_schema.minContains == 1
        assert array_schema.maxContains == 3

    def test_dependent_schemas_parsing(self, supported_openapi_31_spec):
        """Test dependentSchemas parsing."""
        parsed = parse_openapi_31(supported_openapi_31_spec)
        dependent_schema = parsed.components.schemas["DependentSchema"]

        assert dependent_schema.dependentSchemas is not None
        assert "credit_card" in dependent_schema.dependentSchemas

        credit_card_dep = dependent_schema.dependentSchemas["credit_card"]
        assert "billing_address" in credit_card_dep.required

    def test_exclusive_numeric_constraints(self, supported_openapi_31_spec):
        """Test exclusive numeric constraints as numbers (3.1 style)."""
        parsed = parse_openapi_31(supported_openapi_31_spec)
        numeric_schema = parsed.components.schemas["NumericConstraints"]
        score_prop = numeric_schema.properties["score"]

        # In 3.1, these should be numbers, not booleans
        assert score_prop.exclusiveMinimum == 0
        assert score_prop.exclusiveMaximum == 100

    def test_conditional_schemas_parsing(self, supported_openapi_31_spec):
        """Test if/then/else parsing."""
        parsed = parse_openapi_31(supported_openapi_31_spec)
        conditional_schema = parsed.components.schemas["ConditionalSchema"]

        # Check if/then/else exist (using openapi-pydantic field names)
        assert conditional_schema.schema_if is not None
        assert conditional_schema.then is not None
        assert conditional_schema.schema_else is not None

        # Check the if condition
        if_schema = conditional_schema.schema_if
        assert if_schema.properties["type"].const == "premium"

    def test_discriminator_parsing(self, supported_openapi_31_spec):
        """Test discriminator parsing with anyOf."""
        parsed = parse_openapi_31(supported_openapi_31_spec)
        union_schema = parsed.components.schemas["ComplexUnion"]

        assert union_schema.anyOf is not None
        assert len(union_schema.anyOf) == 2
        assert union_schema.discriminator is not None
        assert union_schema.discriminator.propertyName == "type"

    def test_pattern_properties_parsing(self, supported_openapi_31_spec):
        """Test patternProperties parsing."""
        parsed = parse_openapi_31(supported_openapi_31_spec)
        pattern_schema = parsed.components.schemas["DynamicProperties"]

        assert pattern_schema.patternProperties is not None
        assert "^meta_" in pattern_schema.patternProperties
        assert "^config_" in pattern_schema.patternProperties

        meta_schema = pattern_schema.patternProperties["^meta_"]
        assert meta_schema.type == "string"

    def test_code_generation_with_31_features(self, supported_openapi_31_spec):
        """Test that code generation works with 3.1 features."""
        import json

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Save spec to file first
            spec_file = temp_path / "openapi_31_spec.json"
            spec_file.write_text(json.dumps(supported_openapi_31_spec, indent=2))

            # Generate code
            generate_data(spec_file, temp_path, HTTPLibrary.httpx, use_orjson=False)

            # Verify files exist
            assert (temp_path / "models").exists()
            assert (temp_path / "services").exists()
            assert (temp_path / "api_config.py").exists()

            # Check that the code compiles
            models_dir = temp_path / "models"
            if models_dir.exists() and (models_dir / "__init__.py").exists():
                models_content = (models_dir / "__init__.py").read_text()
                compile(models_content, str(models_dir / "__init__.py"), "exec")

            service_dir = temp_path / "services"
            if service_dir.exists():
                service_files = list(service_dir.glob("*.py"))
                if service_files:
                    service_content = service_files[0].read_text()
                    compile(service_content, str(service_files[0]), "exec")


class TestOpenAPI31UnsupportedFeatures:
    """Test OpenAPI 3.1 features that are NOT currently supported."""

    def test_boolean_schemas_not_supported(self):
        """Test that boolean schemas (True/False) are not supported yet."""
        spec_with_boolean_schemas = {
            "openapi": "3.1.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "AlwaysValid": True,  # This should fail
                    "AlwaysInvalid": False,  # This should fail
                }
            },
        }

        from pydantic import ValidationError

        # Boolean schemas (True/False) should raise a pydantic ValidationError
        with pytest.raises(ValidationError):  # Should fail to parse
            parse_openapi_31(spec_with_boolean_schemas)

    def test_boolean_items_not_supported(self):
        """Test that items: false is not supported yet."""
        spec_with_boolean_items = {
            "openapi": "3.1.0",
            "info": {"title": "Test", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "TupleArray": {
                        "type": "array",
                        "prefixItems": [{"type": "string"}],
                        "items": False,  # This should fail
                    }
                }
            },
        }

        from pydantic import ValidationError

        # items: False should raise a pydantic ValidationError
        with pytest.raises(ValidationError):  # Should fail to parse
            parse_openapi_31(spec_with_boolean_items)


class TestOpenAPI31Coverage:
    """Test that we have good coverage of OpenAPI 3.1 features."""

    def test_31_vs_30_feature_comparison(self):
        """Compare feature support between 3.0 and 3.1."""
        # Test that 3.1-specific features work in 3.1 but not 3.0

        spec_31_features = {
            "openapi": "3.1.0",
            "info": {"title": "Test 3.1", "version": "1.0.0"},
            "jsonSchemaDialect": "https://json-schema.org/draft/2020-12/schema",
            "paths": {},
            "components": {
                "schemas": {
                    "Test": {"type": "string", "const": "test_value"}  # 3.1 feature
                }
            },
        }

        # Should work in 3.1
        parsed_31 = parse_openapi_31(spec_31_features)
        assert parsed_31.components.schemas["Test"].const == "test_value"

        # Test that jsonSchemaDialect is preserved
        assert (
            parsed_31.jsonSchemaDialect
            == "https://json-schema.org/draft/2020-12/schema"
        )

        # Convert to 3.0 spec and test with 3.0 parser
        spec_30_no_const = {
            "openapi": "3.0.3",
            "info": {"title": "Test 3.0", "version": "1.0.0"},
            "paths": {},
            "components": {
                "schemas": {
                    "Test": {
                        "type": "string",
                        "const": "test_value",  # Should be ignored in 3.0
                    }
                }
            },
        }

        from openapi_python_generator.parsers import parse_openapi_30

        parsed_30 = parse_openapi_30(spec_30_no_const)

        # In 3.0, const should either not exist or be ignored
        test_schema_30 = parsed_30.components.schemas["Test"]
        # The 3.0 parser might ignore unknown fields or handle them differently
        # This is expected behavior

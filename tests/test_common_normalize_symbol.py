from openapi_python_generator.language_converters.python.common import normalize_symbol


def test_normalize_symbol_keyword_and_chars():
    assert normalize_symbol("class-") == "class_"
    assert normalize_symbol("my$weird$name!") == "myweirdname"

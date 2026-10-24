"""Test schema validation."""

from answer_dataset.pipeline.schema import SchemaHandler


def test_infer_schema():
    example = {"question": "What is X?", "answer": "X is..."}
    schema = SchemaHandler.infer_schema(example)
    assert schema["type"] == "object"
    assert "question" in schema["properties"]
    assert "answer" in schema["properties"]


def test_validate_format():
    valid, error, data = SchemaHandler.validate_format('{"q": "test", "a": "answer"}')
    assert valid
    assert data == {"q": "test", "a": "answer"}


def test_validate_format_invalid():
    valid, error, data = SchemaHandler.validate_format('not json')
    assert not valid
    assert error is not None

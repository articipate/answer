"""Test response validator."""

from answer_dataset.pipeline.validator import ResponseValidator


def test_parse_response_with_rows():
    text = '{"rows": [{"q": "hello", "a": "world"}]}'
    rows, err = ResponseValidator.parse_response(text)
    assert err is None
    assert len(rows) == 1
    assert rows[0]["q"] == "hello"


def test_parse_response_with_code_block():
    text = '```json\n{"rows": [{"q": "test"}]}\n```'
    rows, err = ResponseValidator.parse_response(text)
    assert err is None
    assert len(rows) == 1


def test_extract_json():
    text = 'Some text {"rows": []} more text'
    result = ResponseValidator.extract_json(text)
    assert '"rows"' in result

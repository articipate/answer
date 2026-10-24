"""Test chunker."""

from answer_dataset.documents.chunker import Chunker


def test_chunker_small_text():
    chunker = Chunker()
    text = "Hello world. This is a test."
    chunks = chunker.chunk(text)
    assert len(chunks) == 1
    assert chunks[0] == text


def test_chunker_empty():
    chunker = Chunker()
    chunks = chunker.chunk("")
    assert chunks == []


def test_count_tokens():
    chunker = Chunker()
    tokens = chunker.count_tokens("Hello world")
    assert tokens > 0

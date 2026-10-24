"""Test exporters."""

import json
import csv
import tempfile
import os
from answer_dataset.exporters.jsonl_exporter import JSONLExporter
from answer_dataset.exporters.json_exporter import JSONExporter
from answer_dataset.exporters.csv_exporter import CSVExporter


def test_jsonl_export():
    rows = [{"q": "hello", "a": "world"}, {"q": "foo", "a": "bar"}]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        path = f.name
    try:
        JSONLExporter.export(rows, path)
        with open(path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        assert len(lines) == 2
        assert json.loads(lines[0])["q"] == "hello"
    finally:
        os.unlink(path)


def test_json_export():
    rows = [{"q": "hello", "a": "world"}]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        path = f.name
    try:
        JSONExporter.export(rows, path)
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        assert len(data) == 1
        assert data[0]["a"] == "world"
    finally:
        os.unlink(path)


def test_csv_export():
    rows = [{"q": "hello", "a": "world"}]
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, newline='') as f:
        path = f.name
    try:
        CSVExporter.export(rows, path)
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            data = list(reader)
        assert len(data) == 1
        assert data[0]["q"] == "hello"
    finally:
        os.unlink(path)

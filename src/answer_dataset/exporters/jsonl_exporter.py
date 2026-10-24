"""JSONL exporter."""

import json
from pathlib import Path
from typing import List, Dict, Any


class JSONLExporter:
    @staticmethod
    def export(rows: List[Dict[str, Any]], path: str):
        with open(path, 'w', encoding='utf-8') as f:
            for row in rows:
                f.write(json.dumps(row, ensure_ascii=False) + '\n')
    
    @staticmethod
    def export_from_dataset_rows(dataset_rows, path: str):
        rows = [r.data for r in dataset_rows]
        JSONLExporter.export(rows, path)

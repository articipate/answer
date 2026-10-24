"""JSON exporter."""

import json
from typing import List, Dict, Any


class JSONExporter:
    @staticmethod
    def export(rows: List[Dict[str, Any]], path: str):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, indent=2, ensure_ascii=False)
    
    @staticmethod
    def export_from_dataset_rows(dataset_rows, path: str):
        rows = [r.data for r in dataset_rows]
        JSONExporter.export(rows, path)
